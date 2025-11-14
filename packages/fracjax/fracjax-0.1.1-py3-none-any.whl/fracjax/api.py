import jax
import numpy as np
from typing import Callable, Any, Tuple, Union
from .core.windowing import create_rolling_calculator
from .core.preprocessing import preprocess_series
from .estimators import dfa, wavelet, higuchi, volatility, microstructure, intermarket, entropy
from .utils.progress import run_batched_with_progress

def create_market_microscope(
    method: str = 'dfa',
    window_size: int = 100,
    batch_size: int = 4096,
    progress: bool = False,
    return_diagnostics: bool = False,
    **kwargs
) -> Callable[[np.ndarray], Union[np.ndarray, Tuple[np.ndarray, dict]]]:
    
    preproc_req = "log_returns" 
    
    if method == 'dfa':
        n_values = kwargs.get('n_values', [10, 15, 20, 25, 50])
        kernel_fn = dfa.make_kernel(n_values)
        
    elif method == 'wavelet':
        max_level = kwargs.get('max_level', 4)
        kernel_fn = wavelet.make_kernel(max_level)
        
    elif method == 'higuchi':
        k_max = kwargs.get('k_max', 10)
        kernel_fn = higuchi.make_kernel(k_max)
        preproc_req = "price"
        
    elif method == 'garch':
        kernel_fn = volatility.make_kernel('garch')
        
    elif method == 'semivariance':
        kernel_fn = volatility.make_kernel('semivariance')
        
    elif method == 'cvd':
        kernel_fn = microstructure.make_kernel('cvd')
        preproc_req = "none" 
        
    elif method == 'amihud':
        kernel_fn = microstructure.make_kernel('amihud')
        preproc_req = "none"
        
    elif method == 'coint':
        kernel_fn = intermarket.make_kernel('coint')
        preproc_req = "price" 
        
    elif method == 'lead_lag':
        lag = kwargs.get('lag', 1)
        kernel_fn = intermarket.make_kernel('lead_lag', lag=lag)
        preproc_req = "log_returns" 
        
    elif method == 'entropy_perm':
        m = kwargs.get('m', 3)
        kernel_fn = entropy.make_kernel('permutation', m=m)
        preproc_req = "log_returns"
        
    elif method == 'entropy_hill':
        kernel_fn = entropy.make_kernel('hill')
        preproc_req = "log_returns"
        
    else:
        raise ValueError(f"Unknown method: {method}")

    kernel_vmap = jax.jit(jax.vmap(kernel_fn))
    
    if progress:
        def progress_interface(data: np.ndarray) -> Union[np.ndarray, Tuple[np.ndarray, dict]]:
            if data.ndim == 2 and preproc_req == "log_returns":
                d1 = preprocess_series(data[:, 0], "log_returns")
                d2 = preprocess_series(data[:, 1], "log_returns")
                min_len = min(len(d1), len(d2))
                data_pre = np.stack([d1[:min_len], d2[:min_len]], axis=1)
            elif data.ndim == 2 and preproc_req == "price":
                data_pre = data.astype(np.float32)
            else:
                data_pre = preprocess_series(data, method=preproc_req)

            result = run_batched_with_progress(
                data_pre, 
                kernel_vmap, 
                window_size=window_size, 
                batch_size=batch_size,
                desc=f"Microscope ({method})",
                return_diagnostics=return_diagnostics
            )
            
            if return_diagnostics:
                out, diag = result
                final_out = _pad_output(out, data.shape[0])
                return final_out, diag
            else:
                return _pad_output(result, data.shape[0])
        return progress_interface

    rolling_calc = create_rolling_calculator(
        kernel_fn=kernel_vmap,
        window_size=window_size,
        batch_size=batch_size
    )

    def fast_interface(data: np.ndarray) -> Union[np.ndarray, Tuple[np.ndarray, dict]]:
        if data.ndim == 2 and preproc_req == "log_returns":
            d1 = preprocess_series(data[:, 0], "log_returns")
            d2 = preprocess_series(data[:, 1], "log_returns")
            min_len = min(len(d1), len(d2))
            data_pre = np.stack([d1[:min_len], d2[:min_len]], axis=1)
        elif data.ndim == 2 and preproc_req == "price":
            data_pre = data.astype(np.float32)
        else:
            data_pre = preprocess_series(data, method=preproc_req)

        result = rolling_calc(data_pre)
        final_out = _pad_output(result, data.shape[0])
        
        if return_diagnostics:
            diag = {"method": method, "window": window_size, "mean": float(np.nanmean(final_out))}
            return final_out, diag
        return final_out

    return fast_interface

def _pad_output(result: np.ndarray, total_len: int) -> np.ndarray:
    if result.shape[0] == total_len:
        return result
    final_out = np.full(total_len, np.nan, dtype=np.float32)
    if result.shape[0] > 0:
        final_out[-result.shape[0]:] = np.array(result)
    return final_out
