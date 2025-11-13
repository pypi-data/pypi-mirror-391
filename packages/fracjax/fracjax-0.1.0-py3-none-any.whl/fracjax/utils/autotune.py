# src/your_library/autotune.py
from typing import Sequence, Dict, Any
import numpy as np
from .hurst import create_rolling_hurst_calculator

def auto_tune_hurst(
    series: np.ndarray,
    window_size: int,
    n_values: Sequence[int],
    *,
    min_k_candidates=(4,6,8),
    huber_deltas=(0.5, 0.8, 1.2),
    batch_size: int = 4096,
    sample_prefix: int = 10000
) -> Dict[str, Any]:
    
    L = len(series)
    pref_len = min(L, sample_prefix)
    s_pref = series[:pref_len]

    results = []
    for min_k in min_k_candidates:
        for delta in huber_deltas:
            calc = create_rolling_hurst_calculator(
                window_size=window_size,
                n_values=n_values,
                mode='safe',
                batch_size=batch_size,
                huber_delta=float(delta),
                min_k=int(min_k),
                clip_to_unit=False,
                preprocess="log_returns",
                progress=False,
                return_diagnostics=True
            )
            out, diag = calc(s_pref)
            median = diag.get("median") if diag else None
            nan_frac = diag.get("nan_fraction") if diag else 1.0
            pctgt = diag.get("pct_gt_0.9") if diag else 100.0
            score = (nan_frac * 100.0) * 2.0 + pctgt * 1.0 + (abs((median or 0.0) - 0.5) * 100.0) * 0.8
            results.append({"min_k": int(min_k), "huber_delta": float(delta), "diag": diag, "score": float(score)})

    results_sorted = sorted(results, key=lambda r: r["score"])
    best = results_sorted[0] if results_sorted else None
    return {"best": best, "all": results_sorted}
