import sys
import os
import psutil
import re
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog,
    QMenuBar, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest
from PyQt6.QtCore import QUrl, pyqtSignal, QObject, QTimer, QFileInfo, pyqtSlot
from PyQt6.QtWebChannel import QWebChannel
import requests
from wxswutilsapi import Logger
logger = Logger()

# ---------------- 全局配置（支持端口自定义） ----------------
LOG_FILE = "renderer_watchdog.log"
LOCK_FILE = "raman_app.lock"
DEFAULT_PORT = 8081  # 默认端口
ADMIN_JSON_PATH = "/jsonFile/admin.json"  # 固定路径部分

# ---------------- 工具函数 ----------------
def clean_filename(filename):
    """过滤文件名中的非法字符，替换为下划线"""
    ILLEGAL_CHARS = r'[<>:"/\\|?*]'
    if not filename:
        return "未命名文件"
    cleaned = re.sub(ILLEGAL_CHARS, '_', filename)
    cleaned = cleaned.strip('_')
    return cleaned if cleaned else "未命名文件"

def get_server_config(port=None):
    """获取服务器配置（端口优先级：传入参数 > 命令行 > 默认值）"""
    # 1. 优先使用传入的端口参数
    if port and isinstance(port, int) and 1024 <= port <= 65535:
        current_port = port
    # 2. 其次读取命令行参数（格式：--port=8082 或 -p 8082）
    else:
        current_port = DEFAULT_PORT
        for arg in sys.argv[1:]:
            if arg.startswith('--port='):
                try:
                    current_port = int(arg.split('=')[1])
                    break
                except ValueError:
                    logger.warning(f"命令行端口参数无效：{arg}，使用默认端口{DEFAULT_PORT}")
            elif arg.startswith('-p'):
                try:
                    # 支持 -p 8082 格式（参数后接空格）
                    port_idx = sys.argv.index(arg) + 1
                    if port_idx < len(sys.argv):
                        current_port = int(sys.argv[port_idx])
                        break
                except (ValueError, IndexError):
                    logger.warning(f"命令行端口参数格式错误，使用默认端口{DEFAULT_PORT}")
    
    # 验证端口有效性
    if not (1024 <= current_port <= 65535):
        logger.error(f"端口{current_port}无效（需在1024-65535之间），自动切换为默认端口{DEFAULT_PORT}")
        current_port = DEFAULT_PORT
    
    # 拼接完整URL
    base_url = f"http://localhost:{current_port}/"
    admin_json_url = f"http://localhost:{current_port}{ADMIN_JSON_PATH}"
    return {
        "port": current_port,
        "base_url": base_url,
        "admin_json_url": admin_json_url
    }

# ---------------- JsBridge ----------------
class JsBridge(QObject):
    save_as_signal = pyqtSignal(str, str)

    @pyqtSlot(str, str)
    def saveAs(self, url, fileName):
        cleaned_file_name = clean_filename(fileName)
        self.save_as_signal.emit(url, cleaned_file_name)

# ---------------- 自定义 WebEngineView ----------------
class CustomWebEngineView(QWebEngineView):
    def createWindow(self, type: QWebEnginePage.WebWindowType):
        main_window = self.window()
        new_window = ChildWindow(
            url="about:blank",
            title="新窗口",
            width=1024,
            height=768,
            parent=main_window
        )
        if main_window:
            new_window.window_closed_signal.connect(main_window.remove_child_window)
        new_window.show()
        return new_window.view

# ---------------- 自定义 WebPage ----------------
class CustomWebPage(QWebEnginePage):
    new_window_signal = pyqtSignal(str, str, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = CustomWebEngineView()
        self.view.setPage(self)

    def acceptNavigationRequest(self, url: QUrl, _type: QWebEnginePage.NavigationType, is_main_frame: bool):
        try:
            if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
                pass
        except Exception:
            pass

        if _type == 10:  # 新窗口请求
            width, height = 1024, 768
            width_match = re.search(r'width=(\d+)', url.toString())
            height_match = re.search(r'height=(\d+)', url.toString())
            if width_match:
                width = int(width_match.group(1))
            if height_match:
                height = int(height_match.group(1))
            frame_name = url.fragment() or "新窗口"
            title = frame_name.split("_")[-1] if "_" in frame_name else frame_name
            self.new_window_signal.emit(url.toString(), title, width, height)
            return False
        return super().acceptNavigationRequest(url, _type, is_main_frame)

# ---------------- 子窗口 ----------------
class ChildWindow(QMainWindow):
    window_closed_signal = pyqtSignal(str)

    def __init__(self, url, title, width, height, parent=None):
        super().__init__(parent)
        self.window_title = title
        self.setWindowTitle(title)
        self.resize(width, height)
        self.setMinimumSize(800, 600)

        self.view = CustomWebEngineView()
        self.page = CustomWebPage()
        self.view.setPage(self.page)

        self.bridge = JsBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("electronAPI", self.bridge)
        self.page.setWebChannel(self.channel)

        try:
            self.page.profile().downloadRequested.connect(self.on_download_requested)
        except Exception:
            pass

        if url:
            self.view.setUrl(QUrl(url))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.addWidget(self.view)

        self.center()

    def center(self):
        screen_geo = QApplication.primaryScreen().geometry()
        window_geo = self.frameGeometry()
        window_geo.moveCenter(screen_geo.center())
        self.move(window_geo.topLeft())

    def on_download_requested(self, download: QWebEngineDownloadRequest):
        default_name = download.suggestedFileName() or download.url().fileName() or "未命名文件"
        cleaned_name = clean_filename(default_name)
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", cleaned_name, "All Files (*)"
        )
        if path:
            directory = os.path.dirname(path)
            fileName = clean_filename(os.path.basename(path))
            try:
                download.setDownloadDirectory(directory)
                download.setDownloadFileName(fileName)
                download.accept()
            except Exception:
                try:
                    download.accept()
                except Exception:
                    pass
        else:
            try:
                download.cancel()
            except Exception:
                pass

    def closeEvent(self, event):
        self.window_closed_signal.emit(self.window_title)
        event.accept()

# ---------------- 主窗口（支持端口配置） ----------------
class RamanWebShell(QMainWindow):
    def __init__(self, port=None):
        super().__init__()
        # 初始化服务器配置（端口自定义）
        self.server_config = get_server_config(port)
        self.base_url = self.server_config["base_url"]
        self.admin_json_url = self.server_config["admin_json_url"]

        self.setWindowTitle("拉曼分析")
        self.resize(1500, 900)
        self.setMinimumSize(1500, 900)
        self.child_windows = {}

        central = QWidget()
        self.setCentralWidget(central)
        self.layout = QVBoxLayout(central)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.view = CustomWebEngineView()
        self.page = CustomWebPage()
        self.view.setPage(self.page)
        self.layout.addWidget(self.view)

        self.bridge = JsBridge()
        self.channel = QWebChannel()
        self.channel.registerObject("electronAPI", self.bridge)
        self.page.setWebChannel(self.channel)

        try:
            self.page.profile().downloadRequested.connect(self.on_download_requested)
        except Exception:
            pass
        self.bridge.save_as_signal.connect(self.handle_js_save_as)
        self.page.new_window_signal.connect(self.create_child_window)

        self.init_menu_bar()
        self.init_renderer_monitor()
        self.view.setUrl(QUrl(self.base_url))  # 加载自定义端口的URL
        self.load_app_title()

        if os.path.exists("logo.ico"):
            self.setWindowIcon(QIcon("logo.ico"))

    def init_menu_bar(self):
        menubar = self.menuBar()

    def init_renderer_monitor(self):
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_renderer_status)
        self.monitor_timer.start(60000)

    def load_app_title(self):
        try:
            response = requests.get(self.admin_json_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "config" in data and "appName" in data["config"]:
                    self.setWindowTitle(data["config"]["appName"])
        except Exception as e:
            logger.error(f"加载应用标题失败（端口：{self.server_config['port']}）: {e}")

    def on_download_requested(self, download: QWebEngineDownloadRequest):
        default_name = download.suggestedFileName() or download.url().fileName() or "未命名文件"
        cleaned_name = clean_filename(default_name)
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", cleaned_name, "All Files (*)"
        )
        if path:
            directory = os.path.dirname(path)
            fileName = clean_filename(os.path.basename(path))
            try:
                download.setDownloadDirectory(directory)
                download.setDownloadFileName(fileName)
                download.accept()
            except Exception:
                try:
                    download.accept()
                except Exception:
                    pass
        else:
            try:
                download.cancel()
            except Exception:
                pass

    def handle_js_save_as(self, url, file_name):
        cleaned_file_name = clean_filename(file_name)
        ext = QFileInfo(cleaned_file_name).suffix()
        filters = f"{ext.upper()}文件 (*.{ext});;全部文件 (*.*)" if ext else "全部文件 (*.*)"
        path, _ = QFileDialog.getSaveFileName(self, "另存为", cleaned_file_name, filters)
        if path:
            directory = os.path.dirname(path)
            fileName = clean_filename(os.path.basename(path))
            full_path = os.path.join(directory, fileName)
            try:
                self.page.download(QUrl(url), full_path)
            except Exception:
                try:
                    r = requests.get(url, timeout=10)
                    with open(full_path, "wb") as f:
                        f.write(r.content)
                except Exception as e:
                    logger.error(f"通过 requests 下载失败: {e}")

    def create_child_window(self, url, title, width, height):
        if title not in self.child_windows:
            child = ChildWindow(url, title, width, height, self)
            self.child_windows[title] = child
            child.window_closed_signal.connect(self.remove_child_window)
            child.show()
        else:
            child = self.child_windows[title]
            if child.isMinimized():
                child.showNormal()
            child.raise_()
            child.activateWindow()

    def remove_child_window(self, title):
        if title in self.child_windows:
            window = self.child_windows.pop(title)
            try:
                window.deleteLater()
            except Exception:
                pass

    def check_renderer_status(self):
        try:
            self.page.runJavaScript("true", self.on_renderer_check)
        except Exception as e:
            logger.error(f"渲染进程检查失败: {e}")
            try:
                self.view.reload()
            except Exception:
                pass

    def on_renderer_check(self, result):
        if result is None:
            logger.error("渲染进程无响应，重载页面")
            try:
                self.view.reload()
            except Exception:
                pass

    def closeEvent(self, event):
        event.ignore()

        msg = QMessageBox(self)
        msg.setWindowTitle("确认退出")
        msg.setText("确定要退出应用程序吗？")
        msg.setIcon(QMessageBox.Icon.Question)

        yes_button = msg.addButton("确定", QMessageBox.ButtonRole.YesRole)
        no_button = msg.addButton("取消", QMessageBox.ButtonRole.NoRole)
        msg.setDefaultButton(no_button)

        msg.exec()

        if msg.clickedButton() == yes_button:
            for window in list(self.child_windows.values()):
                try:
                    if not window.isDestroyed():
                        window.close()
                except Exception:
                    pass

            self.child_windows.clear()
            try:
                self.monitor_timer.stop()
            except Exception:
                pass

            event.accept()

# ---------------- 单实例 ----------------
def is_single_instance():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                QMessageBox.warning(None, "提示", "应用已在运行中！")
                return False
            else:
                os.remove(LOCK_FILE)
        except (ValueError, OSError):
            try:
                os.remove(LOCK_FILE)
            except Exception:
                pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True

# ---------------- 对外暴露的启动函数 ----------------
def start_box(port=None):
    """
    启动拉曼分析应用
    :param port: 自定义端口号（1024-65535），默认8081
    """
    app = QApplication(sys.argv)
    if not is_single_instance():
        return
    # 传入端口参数初始化主窗口
    window = RamanWebShell(port=port)
    window.show()
    result = app.exec()
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass
    sys.exit(result)