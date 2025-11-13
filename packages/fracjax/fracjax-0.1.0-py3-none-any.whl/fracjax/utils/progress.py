import numpy as np
from tqdm.auto import tqdm
import jax

def _make_windows_host(slice_arr: np.ndarray, window_size: int) -> np.ndarray:
    return np.lib.stride_tricks.sliding_window_view(slice_arr, window_size)

def run_batched_with_progress(series: np.ndarray, kernel_jitted, window_size: int, batch_size: int = 4096, desc: str = "Processing", return_diagnostics: bool = False):
    series = np.asarray(series)
    L = series.shape[0]
    if L < window_size:
        out = np.full((L,), np.nan, dtype=np.float32)
        if return_diagnostics:
            return out, {"num_windows": 0}
        return out

    num_windows = L - window_size + 1
    num_batches = (num_windows + batch_size - 1) // batch_size
    out_windows = np.full((num_windows,), np.nan, dtype=np.float32)
    
    collected_vals = []
    
    for b in tqdm(range(num_batches), desc=desc, unit="batch"):
        start_w = b * batch_size
        n_w = min(batch_size, num_windows - start_w)
        series_start = start_w
        series_slice_len = n_w + window_size - 1
        series_slice = series[series_start: series_start + series_slice_len]
        
        windows_batch = _make_windows_host(series_slice, window_size).astype(np.float32)
        windows_dev = jax.device_put(windows_batch)
        
        res_jnp = kernel_jitted(windows_dev)
        res = np.array(res_jnp.block_until_ready())
        
        out_windows[start_w:start_w + n_w] = res[:n_w]
        
        if return_diagnostics:
            valid = ~np.isnan(res)
            if valid.any():
                collected_vals.append(res[valid])

    pad = np.full((window_size - 1,), np.nan, dtype=np.float32)
    out = np.concatenate([pad, out_windows])

    if not return_diagnostics:
        return out

    all_vals = np.concatenate(collected_vals) if collected_vals else np.array([], dtype=np.float32)
    diag = {
        "num_windows": num_windows,
        "mean": float(np.nanmean(all_vals)) if all_vals.size else None,
        "median": float(np.nanmedian(all_vals)) if all_vals.size else None
    }
    return out, diag