import jax.numpy as jnp
import jax
from ..math.regression import theil_sen_slope

def _higuchi_length(series: jnp.ndarray, k: int) -> jnp.ndarray:
    n = series.shape[0]
    diffs = jnp.abs(series[k:] - series[:-k])
    L_k = jnp.sum(diffs) * (n - 1) / (k * (n - k) ** 2)
    return L_k

def make_kernel(k_max: int = 10):
    k_values = jnp.arange(1, k_max + 1, dtype=jnp.float32)
    log_k = jnp.log(1.0 / k_values)

    def kernel(window_data: jnp.ndarray) -> jnp.ndarray:
        lengths = []
        for k in range(1, k_max + 1):
            lengths.append(_higuchi_length(window_data, k))
            
        log_L = jnp.log(jnp.stack(lengths) + 1e-12)
        return theil_sen_slope(log_k, log_L)
        
    return kernel