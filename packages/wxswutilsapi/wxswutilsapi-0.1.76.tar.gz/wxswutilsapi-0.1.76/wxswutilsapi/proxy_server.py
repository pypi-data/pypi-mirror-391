from flask import Flask, send_file, request, Response, jsonify
import os
import mimetypes
import requests
from datetime import datetime, timedelta
from werkzeug.serving import run_simple
import threading
import socket
from wxswutilsapi import Logger
logger = Logger()
# ========================
# 默认配置
# ========================
STATIC_FOLDER = os.path.abspath("dist")   # Vue/React打包路径
JSON_FOLDER = os.path.abspath("jsonDataSave")

# 默认 API 地址（可在 start_proxy 时动态修改）
API_ADMIN_MC = "http://127.0.0.1:55502"
API_MULTICHANEL = "http://127.0.0.1:56883"

# Flask 应用
app = Flask(__name__)

# ========================
# 缓存配置
# ========================
CACHE_TIME = 3600 * 12  # 12小时缓存
CACHE_EXT = {".js", ".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2"}

def set_headers(response):
    """统一跨域与缓存设置"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


# ========================
# 静态文件服务 + SPA 支持
# ========================
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path):
    full_path = os.path.join(STATIC_FOLDER, path)

    # ---- 处理静态文件 ----
    if path and os.path.isfile(full_path):
        ext = os.path.splitext(full_path)[1].lower()
        mime_type = mimetypes.guess_type(full_path)[0] or "application/octet-stream"
        response = send_file(full_path, mimetype=mime_type)

        if ext in CACHE_EXT:
            # 缓存静态资源
            response.headers["Cache-Control"] = f"public, max-age={CACHE_TIME}"
            expire_time = datetime.utcnow() + timedelta(seconds=CACHE_TIME)
            response.headers["Expires"] = expire_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        else:
            response.headers["Cache-Control"] = "no-store"
        return set_headers(response)

    # ---- 子目录 index.html ----
    sub_index = os.path.join(STATIC_FOLDER, path, "index.html")
    if os.path.exists(sub_index):
        response = send_file(sub_index, mimetype="text/html")
        return set_headers(response)

    # ---- 根目录 index.html ----
    index_path = os.path.join(STATIC_FOLDER, "index.html")
    if os.path.exists(index_path):
        response = send_file(index_path, mimetype="text/html")
        return set_headers(response)

    return jsonify({"error": "File not found"}), 404


# ========================
# JSON 文件访问
# ========================
@app.route("/jsonFile/<path:filename>")
def serve_json(filename):
    file_path = os.path.join(JSON_FOLDER, filename)
    if not os.path.isfile(file_path):
        return jsonify({"error": "File not found"}), 404
    response = send_file(file_path, mimetype="application/json")
    return set_headers(response)


# ========================
# API 代理
# ========================
def proxy_request(target_url):
    try:
        method = request.method
        data = request.get_data()
        params = request.args
        headers = {k: v for k, v in request.headers if k.lower() not in ["host", "content-length", "connection"]}
        path = request.path
        url = f"{target_url}{path}"

        resp = requests.request(method, url, headers=headers, data=data, params=params, timeout=20)
        response = Response(resp.content, resp.status_code)
        for k, v in resp.headers.items():
            if k.lower() not in ["content-encoding", "transfer-encoding", "connection"]:
                response.headers[k] = v
        return set_headers(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api-admin-mc/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def proxy_admin(path):
    return proxy_request(API_ADMIN_MC)


@app.route("/api-multichanel/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def proxy_multi(path):
    return proxy_request(API_MULTICHANEL)


# ========================
# 测试接口
# ========================
@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})


# ========================
# 启动逻辑
# ========================
def is_port_in_use(port):
    """检测端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def run(port):
    """在后台线程启动 Flask"""
    logger.info(f"🚀 启动 Flask 代理服务：http://127.0.0.1:{port}")
    run_simple("0.0.0.0", port, app, threaded=True)


def start_proxy(admin_port=55502, api_port=56883, proxy_port=8081):
    """
    启动本地代理服务器

    参数：
    ----------
    admin_port : int
        后端 API_ADMIN_MC 端口
    api_port : int
        后端 API_MULTICHANEL 端口
    proxy_port : int
        本地 Flask 代理端口（默认8081）
    """
    global API_ADMIN_MC, API_MULTICHANEL

    API_ADMIN_MC = f"http://127.0.0.1:{admin_port}"
    API_MULTICHANEL = f"http://127.0.0.1:{api_port}"

    if is_port_in_use(proxy_port):
        logger.info(f"⚠️ 端口 {proxy_port} 已被占用，代理服务未启动")
        return

    proxy_thread = threading.Thread(target=run, args=(proxy_port,), daemon=True)
    proxy_thread.start()
    logger.info(f"✅ 代理服务已启动：")
    logger.info(f"   → Proxy URL: http://127.0.0.1:{proxy_port}")
    logger.info(f"   → Admin API: {API_ADMIN_MC}")
    logger.info(f"   → Multi API: {API_MULTICHANEL}")
