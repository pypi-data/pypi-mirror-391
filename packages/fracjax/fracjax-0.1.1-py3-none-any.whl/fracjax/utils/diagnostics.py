from typing import Dict, Iterable, Any
import numpy as np

def summary_stats(arr: np.ndarray) -> Dict[str, Any]:
    arr = np.asarray(arr, dtype=np.float64)
    mask = ~np.isnan(arr)
    valid = arr[mask]
    return {
        "count": int(arr.size),
        "nan_fraction": float(1.0 - (mask.sum() / max(1, arr.size))),
        "median": float(np.nanmedian(arr)) if valid.size else None,
        "mean": float(np.nanmean(arr)) if valid.size else None,
        "std": float(np.nanstd(arr)) if valid.size else None,
        "min": float(np.nanmin(arr)) if valid.size else None,
        "max": float(np.nanmax(arr)) if valid.size else None,
        "pct_gt_0.9": float((valid > 0.9).mean() * 100.0) if valid.size else None
    }

def correlation_with_forward_returns(prices: np.ndarray, feature: np.ndarray, horizons: Iterable[int] = (1, 5, 21)) -> Dict[int, float]:
    p = np.asarray(prices, dtype=np.float64)
    feat = np.asarray(feature, dtype=np.float64)
    Lp = p.shape[0]
    Lf = feat.shape[0]
    if Lf == Lp:
        offset = 0
    elif Lf == Lp - 1:
        offset = 1
    else:
        offset = Lp - Lf
    logp = np.log(p + 1e-12)
    out = {}
    for h in horizons:
        if h < 1 or h >= Lp:
            out[h] = None
            continue
        fwd = logp[h:] - logp[:-h]
        max_t = Lp - h
        feat_indices = np.arange(max_t) - offset
        valid_idx_mask = (feat_indices >= 0) & (feat_indices < Lf)
        if not np.any(valid_idx_mask):
            out[h] = None
            continue
        fwd_sel = fwd[valid_idx_mask]
        feat_sel = feat[feat_indices[valid_idx_mask]]
        mask = (~np.isnan(fwd_sel)) & (~np.isnan(feat_sel))
        if mask.sum() < 2:
            out[h] = None
            continue
        try:
            corr = float(np.corrcoef(feat_sel[mask], fwd_sel[mask])[0, 1])
        except Exception:
            corr = None
        out[h] = corr
    return out