import jax
import jax.numpy as jnp
from jax.lax import dynamic_slice
from typing import Callable

def create_rolling_calculator(
    kernel_fn: Callable[[jnp.ndarray], jnp.ndarray],
    window_size: int,
    batch_size: int = 4096
) -> Callable[[jnp.ndarray], jnp.ndarray]:
    
    kernel_jit = jax.jit(kernel_fn)

    def _process_batch(series_segment: jnp.ndarray) -> jnp.ndarray:
        L = series_segment.shape[0]
        num_windows = L - window_size + 1
        
        if num_windows <= 0:
            return jnp.array([], dtype=jnp.float32)
        
        indices = jnp.arange(num_windows)
        
        
        ndim = series_segment.ndim
        base_slice_sizes = (window_size,) + series_segment.shape[1:]
        
        def _get_window(i):
            start_indices = (i,) + (0,) * (ndim - 1)
            return dynamic_slice(series_segment, start_indices, base_slice_sizes)
            
     
        windows = jax.vmap(_get_window)(indices)
        return kernel_jit(windows)

    def rolling_apply(series: jnp.ndarray) -> jnp.ndarray:
        series_jnp = jnp.asarray(series, dtype=jnp.float32)
        
        total_len = series_jnp.shape[0]
        
        if total_len < window_size:
            return jnp.full((total_len,), jnp.nan, dtype=jnp.float32)

        valid_len = total_len - window_size + 1
        results_list = []
        
        ndim = series_jnp.ndim
        rest_shape = series_jnp.shape[1:]
        
        for i in range(0, valid_len, batch_size):
            end_idx = min(i + batch_size, valid_len)
            segment_len = (end_idx - i) + window_size - 1
            
            start_indices = (i,) + (0,) * (ndim - 1)
            slice_sizes = (segment_len,) + rest_shape
            
            segment = dynamic_slice(series_jnp, start_indices, slice_sizes)
            res = _process_batch(segment)
            results_list.append(res)
            
        if not results_list:
             return jnp.full((total_len,), jnp.nan, dtype=jnp.float32)

        valid_results = jnp.concatenate(results_list)
        
        pad = jnp.full((window_size - 1,), jnp.nan, dtype=jnp.float32)
        return jnp.concatenate([pad, valid_results])

    return rolling_apply