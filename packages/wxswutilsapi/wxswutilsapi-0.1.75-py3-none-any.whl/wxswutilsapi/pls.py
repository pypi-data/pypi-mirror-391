import numpy as np
from sklearn.calibration import cross_val_predict
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import pandas as pd
from typing import Tuple, Optional
from sklearn.model_selection import KFold

def optimise_pls_cv(n_components,x, y, n_comp):
    try:
        mse = []
        if n_components == 0:
            component = np.arange(1, n_comp)
            for i in component:
                pls = PLSRegression(n_components=i)
                y_cv = cross_val_predict(pls, x, y, cv=8)
                mse.append(mean_squared_error(y, y_cv))
            MSE_MIN = np.argmin(mse)
            MSE_MIN += 1
            pass
        else:
            MSE_MIN = n_components
            pass
        pls_opt = PLSRegression(n_components=MSE_MIN)
        y, x = zip(*[(a, b) for a, b in zip(y, x) if a is not None])
        y=list(y)
        x=list(x)
        pls_opt.fit(x, y)
        return pls_opt, pls_opt.predict(x),MSE_MIN
    except Exception as e:
        raise ValueError(f"optimise_pls_cv:{str(e)}") from e
    
def optimise_pls_cv_jx(n_components, x, y, n_comp, test_size=0.3, random_state=42):
    try:
        # 1. 过滤无效样本
        filtered = [(a, b) for a, b in zip(y, x) if a is not None]
        if not filtered:
            raise ValueError("No valid samples after filtering (y contains None)")
        y_filtered, x_filtered = zip(*filtered)
        y_filtered = np.array(y_filtered)
        x_filtered = np.array(x_filtered)
        
        # 2. 拆分训练集和验证集
        x_train, x_val, y_train, y_val = train_test_split(
            x_filtered, y_filtered,
            test_size=test_size,
            random_state=random_state
        )
        
        # 3. 确定主成分数量并计算验证集指标（重点：直接计算RMSE）
        if n_components == 0:
            components = np.arange(1, n_comp)
            rmse_list = []  # 直接存储RMSE，不再用MSE列表
            r2_list = []
            for i in components:
                pls = PLSRegression(n_components=i)
                pls.fit(x_train, y_train)
                y_pred_val = pls.predict(x_val)
                y_pred_val_list = y_pred_val.tolist()
                
                # 直接计算RMSE（使用root_mean_squared_error）
                current_rmse = root_mean_squared_error(y_val, y_pred_val_list)
                current_r2 = r2_score(y_pred_val_list, y_val)
                rmse_list.append(current_rmse)
                r2_list.append(current_r2)
            
            # 选RMSE最小的主成分数（更直接）
            opt_idx = np.argmin(rmse_list)
            MSE_MIN = components[opt_idx]
            val_rmse = rmse_list[opt_idx]  # 直接取最小RMSE
            val_r2 = r2_list[opt_idx]
        
        else:
            MSE_MIN = n_components
            pls = PLSRegression(n_components=MSE_MIN)
            pls.fit(x_train, y_train)
            y_pred_val = pls.predict(x_val)
            y_pred_val_list = y_pred_val.tolist()
            
            # 直接计算RMSE
            val_rmse = root_mean_squared_error(y_val, y_pred_val_list)
            val_r2 = r2_score(y_pred_val_list, y_val)
        
        # 4. 全量数据训练最终模型
        pls_opt = PLSRegression(n_components=MSE_MIN)
        pls_opt.fit(x_filtered, y_filtered)
        y_pred_full = pls_opt.predict(x_filtered)
        
        # 返回：模型、全量预测、主成分数、验证集RMSE、验证集R²
        return pls_opt, y_pred_full, MSE_MIN, val_rmse, val_r2
    
    except Exception as e:
        raise ValueError(f"optimise_pls_cv: {str(e)}") from e

def optimise_pls_cv_jx_scale(
    n_components, x, y, n_comp, test_size=0.3, random_state=42, scale: bool = True
):
    try:
        # 1. 过滤无效样本（移除y为None的样本）
        filtered = [(a, b) for a, b in zip(y, x) if a is not None]
        if not filtered:
            raise ValueError("No valid samples after filtering (y contains None)")
        y_filtered, x_filtered = zip(*filtered)
        y_filtered = np.array(y_filtered)
        x_filtered = np.array(x_filtered)

        # 2. 根据 test_size 决定是否划分
        if test_size == 0:
            x_train, y_train = x_filtered, y_filtered
            x_val, y_val = None, None
        else:
            if not (0 < test_size < 1):
                raise ValueError("test_size must be in (0, 1) when greater than 0")
            x_train, x_val, y_train, y_val = train_test_split(
                x_filtered, y_filtered,
                test_size=test_size,
                random_state=random_state
            )

        # 3. 确定主成分数量并计算验证集指标
        val_rmse = None
        val_r2 = None

        if n_components == 0:
            # 自动优化成分数（需要验证集）
            if test_size == 0:
                raise ValueError("n_components=0 requires test_size>0 for validation")
            components = np.arange(1, n_comp)
            rmse_list, r2_list = [], []
            for i in components:
                pls = Pipeline([
                    ('scaler', StandardScaler()),
                    ('pls', PLSRegression(n_components=i))
                ]) if scale else PLSRegression(n_components=i)
                pls.fit(x_train, y_train)
                y_pred_val = pls.predict(x_val)
                rmse_list.append(root_mean_squared_error(y_val, y_pred_val))
                r2_list.append(r2_score(y_val, y_pred_val))
            opt_idx = np.argmin(rmse_list)
            MSE_MIN = components[opt_idx]
            val_rmse = rmse_list[opt_idx]
            val_r2 = r2_list[opt_idx]
        else:
            MSE_MIN = n_components

        # 4. 最终模型训练
        pls_opt = Pipeline([
            ('scaler', StandardScaler()),
            ('pls', PLSRegression(n_components=MSE_MIN))
        ]) if scale else PLSRegression(n_components=MSE_MIN)

        pls_opt.fit(x_train, y_train)
        y_pred_full = pls_opt.predict(x_train)

        # ✅ 若没有验证集（test_size==0），使用训练集作为自验证
        if test_size == 0:
            val_rmse = root_mean_squared_error(y_train, y_pred_full)
            val_r2 = r2_score(y_train, y_pred_full)
        elif test_size > 0 and n_components != 0:
            # 固定成分时仍然计算验证集指标
            y_pred_val = pls_opt.predict(x_val)
            val_rmse = root_mean_squared_error(y_val, y_pred_val)
            val_r2 = r2_score(y_val, y_pred_val)

        return pls_opt, y_pred_full, MSE_MIN, val_rmse, val_r2

    except Exception as e:
        raise ValueError(f"optimise_pls_cv_jx_scale: {str(e)}") from e
    


def optimise_pls_cv_jx_scale2(
    n_components,
    x,
    y,
    n_comp,
    test_size=0.3,
    random_state=42,
    scale: bool = True,
    x_val_external=None,
    y_val_external=None,  # ✅ 新增：允许外部传入验证集
):
    """
    优化 PLS 主成分数，支持两种训练-验证集划分方式：
    1. 随机划分（默认，使用 test_size）
    2. 外部传入验证集（x_val_external, y_val_external）

    参数：
        n_components: 固定主成分数；若为 0，则自动优化。
        x, y: 训练数据（numpy 数组或可转为数组的结构）
        n_comp: 最大主成分候选数（仅在 n_components=0 时使用）
        test_size: 测试集比例；为 0 表示使用训练集自验证
        random_state: 随机数种子
        scale: 是否标准化输入数据
        x_val_external, y_val_external: 外部提供的验证集

    返回：
        pls_opt: 最优 PLS 模型（或含标准化的 Pipeline）
        y_pred_full: 训练集预测结果
        MSE_MIN: 最优主成分数
        val_rmse: 验证集 RMSE
        val_r2: 验证集 R²
    """
    try:
        # 1️⃣ 过滤无效样本
        filtered = [(a, b) for a, b in zip(y, x) if a is not None]
        if not filtered:
            raise ValueError("No valid samples after filtering (y contains None)")
        y_filtered, x_filtered = zip(*filtered)
        y_filtered = np.array(y_filtered)
        x_filtered = np.array(x_filtered)

        # 2️⃣ 划分数据集（支持外部验证集）
        if x_val_external is not None and y_val_external is not None:
            # ---- 外部传入验证集 ----
            x_train, y_train = x_filtered, y_filtered
            x_val, y_val = np.array(x_val_external), np.array(y_val_external)
            external_split = True
        elif test_size == 0:
            # ---- 自验证模式 ----
            x_train, y_train = x_filtered, y_filtered
            x_val, y_val = None, None
            external_split = False
        else:
            # ---- 随机划分 ----
            if not (0 < test_size < 1):
                raise ValueError("test_size must be in (0, 1) when greater than 0")
            x_train, x_val, y_train, y_val = train_test_split(
                x_filtered, y_filtered,
                test_size=test_size,
                random_state=random_state
            )
            external_split = False

        # 3️⃣ 自动优化主成分数（若 n_components==0）
        val_rmse = None
        val_r2 = None

        if n_components == 0:
            if (test_size == 0) and not external_split:
                raise ValueError("n_components=0 requires validation data (test_size>0 or external)")
            components = np.arange(1, n_comp)
            rmse_list, r2_list = [], []

            for i in components:
                pls = Pipeline([
                    ('scaler', StandardScaler()),
                    ('pls', PLSRegression(n_components=i))
                ]) if scale else PLSRegression(n_components=i)

                pls.fit(x_train, y_train)
                y_pred_val = pls.predict(x_val)
                rmse_list.append(root_mean_squared_error(y_val, y_pred_val))
                r2_list.append(r2_score(y_val, y_pred_val))

            opt_idx = np.argmin(rmse_list)
            MSE_MIN = components[opt_idx]
            val_rmse = rmse_list[opt_idx]
            val_r2 = r2_list[opt_idx]
        else:
            MSE_MIN = n_components

        # 4️⃣ 使用最优主成分重新训练
        pls_opt = Pipeline([
            ('scaler', StandardScaler()),
            ('pls', PLSRegression(n_components=MSE_MIN))
        ]) if scale else PLSRegression(n_components=MSE_MIN)

        pls_opt.fit(x_train, y_train)
        y_pred_full = pls_opt.predict(x_train)

        # 5️⃣ 计算验证指标
        if test_size == 0 and not external_split:
            # ✅ 自验证（训练集自身）
            val_rmse = root_mean_squared_error(y_train, y_pred_full)
            val_r2 = r2_score(y_train, y_pred_full)
        elif (test_size > 0 or external_split) and n_components != 0:
            # ✅ 有验证集时
            y_pred_val = pls_opt.predict(x_val)
            val_rmse = root_mean_squared_error(y_val, y_pred_val)
            val_r2 = r2_score(y_val, y_pred_val)

        return pls_opt, y_pred_full, MSE_MIN, val_rmse, val_r2

    except Exception as e:
        raise ValueError(f"optimise_pls_cv_jx_scale2: {str(e)}") from e

def _snv(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """行向标准正态变换 SNV"""
    mu = np.nanmean(X, axis=1, keepdims=True)
    sd = np.nanstd(X, axis=1, keepdims=True)
    return (X - mu) / (sd + eps)


def _hat_diag(X: np.ndarray) -> np.ndarray:
    """计算杠杆值（Hat 矩阵对角线）"""
    XtX = X.T @ X
    ridge = 1e-6 * np.trace(XtX) / max(1, X.shape[1])
    H = X @ np.linalg.pinv(XtX + ridge * np.eye(X.shape[1])) @ X.T
    return np.clip(np.diag(H), 0.0, 1.0)


def _cv_pls_predict(X: np.ndarray, y: np.ndarray, n_components: int,
                    n_splits: int = 5, random_state: int = 42) -> np.ndarray:
    """K 折交叉验证预测（返回一维 y_pred）"""
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    y_pred = np.zeros_like(y, dtype=float)
    pls = PLSRegression(n_components=n_components, scale=False)
    y2d = y.reshape(-1, 1)
    for tr, te in kf.split(X):
        pls.fit(X[tr], y2d[tr])
        y_pred[te] = pls.predict(X[te]).ravel()
    return y_pred


def _choose_ncomp(X: np.ndarray, y: np.ndarray, max_pls: int = 12,
                  n_splits: int = 5, random_state: int = 42) -> int:
    """自动选择最优 PLS 组分"""
    upper = int(min(max_pls, X.shape[1] - 1, max(2, (X.shape[0] - 1) // 2)))
    best_n, best_rmse = 2, np.inf
    for n in range(2, max(upper, 2) + 1):
        yhat = _cv_pls_predict(X, y, n, n_splits=n_splits, random_state=random_state)
        r = float(np.sqrt(mean_squared_error(y, yhat)))
        if r < best_rmse:
            best_rmse, best_n = r, n
    return int(best_n)


def _to_numeric_2d(arr) -> np.ndarray:
    """强制转换为 2D 数值矩阵，无法转换的元素记为 NaN"""
    if isinstance(arr, np.ndarray):
        A = arr
    else:
        A = np.asarray(arr, dtype=object)
    if A.ndim == 1:
        A = A.reshape(-1, 1)
    df = pd.DataFrame(A).apply(pd.to_numeric, errors='coerce')
    return df.values.astype(float)


def _to_numeric_1d(vec) -> np.ndarray:
    """强制转换为 1D 数值向量"""
    if isinstance(vec, np.ndarray):
        v = vec.reshape(-1)
    else:
        v = np.asarray(vec, dtype=object).reshape(-1)
    s = pd.to_numeric(pd.Series(v), errors='coerce')
    return s.values.astype(float)


def _z(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """稳健 z 分数（样本均值/样本标准差）"""
    m = np.nanmean(x)
    s = np.nanstd(x)
    return (x - m) / (s + eps)


# ---------------------- 主函数 ----------------------

def select_influential_samples(
    y,
    X,
    n_splits: int = 5,
    leverage_q: float = 0.95, # 杠杆阈值
    resid_q: float = 0.95, # |标准化残差| 阈值
    max_pls: int = 12, # 最大组分数量
    auto_tune: bool = True, # 自动寻优 PLS 组分
    apply_snv: bool = True, # 行向 SNV 预处理
    random_state: int = 42, #随机种子
    n_remove: Optional[int] = None  # 控制删除点个数；None 表示用阈值法
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    选择对回归分析影响显著的样本。

    参数：
    --------
    y : array-like
        化效向量，可为 object/字符串，将自动转为数值。
    X : array-like
        光谱矩阵。
    leverage_q : float
        杠杆阈值分位数（默认 0.95）。
    resid_q : float
        标准化残差阈值分位数（默认 0.95）。
    n_remove : Optional[int]
        - None：不开启 Top-k，采用原“阈值法”（高杠杆或高残差）删除；
        - 非负整数 k：采用 Top-k 法，删除异常分数最高的 k 个样本。

    返回：
    --------
    X_clean : 剔除异常样本后的光谱矩阵
    y_clean : 剔除异常样本后的化效向量
    outliers_df : 异常样本及其评价指标表（含选择模式与异常分数）
    """
    # 输入与清洗
    y = _to_numeric_1d(y)
    X = _to_numeric_2d(X)
    if X.shape[0] != y.shape[0]:
        raise ValueError(f"X 与 y 的样本数不一致: X={X.shape[0]}, y={y.shape[0]}")

    n_samples = X.shape[0]
    if n_samples < 10:
        raise ValueError("样本数过少（<10），不建议做此类诊断。")

    valid_y = np.isfinite(y)
    X = X[valid_y]
    y = y[valid_y]
    kept_idx = np.where(valid_y)[0]

    col_med = np.nanmedian(X, axis=0)
    if np.any(~np.isfinite(col_med)):
        raise ValueError("X 存在整列无法转换为数值（全 NaN）")
    mask = ~np.isfinite(X)
    if mask.any():
        X[mask] = col_med[np.where(mask)[1]]

    # 预处理
    X_proc = _snv(X) if apply_snv else X.copy()

    # 选择 PLS 组分
    n_comp = _choose_ncomp(X_proc, y, max_pls=max_pls, n_splits=n_splits,
                           random_state=random_state) if auto_tune else max(2, min(10, X_proc.shape[1] - 1))

    # 计算残差、杠杆、标准化残差
    y_pred = _cv_pls_predict(X_proc, y, n_components=n_comp, n_splits=n_splits, random_state=random_state)
    resid = y - y_pred
    h = _hat_diag(X_proc)

    dof = max(1, min(X_proc.shape[1], X_proc.shape[0] - n_comp - 1))
    s2 = np.var(resid, ddof=dof)
    stud = resid / np.sqrt(s2 * (1 - h) + 1e-12)

    # 两种“删除策略”
    mode = "threshold"
    if n_remove is None:
        #  阈值法：高杠杆或高残差即异常
        lev_thr = float(np.quantile(h, leverage_q))
        stud_thr = float(np.quantile(np.abs(stud), resid_q))
        outlier_flag = (h > lev_thr) | (np.abs(stud) > stud_thr)
        out_idx_local = np.where(outlier_flag)[0]
        score = _z(np.abs(stud)) + _z(h)  
    else:
        #  Top-k 法：删除 n_remove 个（n_remove 可为 0）
        mode = "top-k"
        k = int(max(0, n_remove))
        # 综合异常分数：z(|stud|) + z(h)（等权）
        # score = _z(np.abs(stud)) + _z(h)
        # 综合异常分数：z(|stud|) + z(h)（加权）
        score = 0.2 * _z(np.abs(stud)) + 0.8 * _z(h)

        order = np.argsort(-score)  # 从高到低
        out_idx_local = order[:min(k, X.shape[0]-1)]  # 至少保留 1 个样本
        # 给“阈值列”返回信息性数值（不用于筛选）
        lev_thr = float(np.quantile(h, leverage_q))
        stud_thr = float(np.quantile(np.abs(stud), resid_q))

    out_idx_global = kept_idx[out_idx_local]

    # 输出表
    outliers_df = pd.DataFrame({
        "原始索引": out_idx_global,
        "残差": resid[out_idx_local],
        "标准化残差": stud[out_idx_local],
        "杠杆值": h[out_idx_local],
        "异常分数": score[out_idx_local],
        "高杠杆(阈值法)": h[out_idx_local] > lev_thr,
        "高残差(阈值法)": np.abs(stud[out_idx_local]) > stud_thr,
        "PLS组分": n_comp,
        "杠杆阈值": lev_thr,
        "标准化残差阈值": stud_thr,
        "选择模式": mode
    }).sort_values("异常分数", ascending=False if mode == "top-k" else True
    ).sort_values("标准化残差", key=np.abs, ascending=False
    ).reset_index(drop=True)

    # 删除异常后的数据
    keep_local = np.ones_like(y, dtype=bool)
    keep_local[out_idx_local] = False
    X_clean = X[keep_local]
    y_clean = y[keep_local]

    return X_clean, y_clean, outliers_df