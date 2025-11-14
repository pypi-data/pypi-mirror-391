from typing import Literal
import numpy as np

PreprocMethod = Literal["none", "price", "log_price", "returns", "log_returns", "detrend", "demean", "auto"]
EPS = 1e-12

def _safe_log(x: np.ndarray) -> np.ndarray:
    return np.log(x + EPS)

def preprocess_series(
    series: np.ndarray,
    method: PreprocMethod = "log_returns",
    detrend_degree: int = 1
) -> np.ndarray:
   
    s = np.asarray(series, dtype=np.float64)
    if method in ("none", "price"):
        return s.astype(np.float32)

    if method == "log_price":
        return _safe_log(s).astype(np.float32)

    if method in ("returns", "log_returns", "auto"):
        if method == "returns":
            return np.diff(s).astype(np.float32)
        if np.any(s <= 0):
            return np.diff(s).astype(np.float32)
        return np.diff(_safe_log(s)).astype(np.float32)

    if method == "demean":
        return (s - np.nanmean(s)).astype(np.float32)

    if method == "detrend":
        idx = np.arange(s.shape[0])
        mask = ~np.isnan(s)
        if mask.sum() < (detrend_degree + 1):
            return (s - np.nanmean(s)).astype(np.float32)
        coefs = np.polyfit(idx[mask], s[mask], detrend_degree)
        trend = np.polyval(coefs, idx)
        return (s - trend).astype(np.float32)

    return s.astype(np.float32)
