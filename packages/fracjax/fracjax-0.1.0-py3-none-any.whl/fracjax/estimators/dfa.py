import jax.numpy as jnp
import jax
from ..math.regression import theil_sen_slope

def _fluctuation_function(profile: jnp.ndarray, n: int) -> jnp.ndarray:
    L = profile.shape[0]
    num_segments = L // n
    length_used = num_segments * n
    profile_trimmed = profile[:length_used]
    segments = profile_trimmed.reshape((num_segments, n))
    
    x = jnp.arange(n, dtype=jnp.float32)
    mean_x = jnp.mean(x)
    mean_y = jnp.mean(segments, axis=1, keepdims=True)
    
    num = jnp.sum((segments - mean_y) * (x - mean_x), axis=1)
    den = jnp.sum((x - mean_x)**2)
    
    slope = num / (den + 1e-12)
    intercept = mean_y.squeeze() - slope * mean_x
    
    trend = slope[:, None] * x[None, :] + intercept[:, None]
    rms = jnp.sqrt(jnp.mean((segments - trend)**2, axis=1))
    return jnp.sqrt(jnp.mean(rms**2))

def make_kernel(n_values):
    n_list = [int(x) for x in n_values]
    log_n = jnp.log(jnp.array(n_list, dtype=jnp.float32))

    def kernel(window_data: jnp.ndarray) -> jnp.ndarray:
        profile = jnp.cumsum(window_data - jnp.mean(window_data))
        f_values = []
        for n in n_list:
            f_values.append(_fluctuation_function(profile, n))
        
        f_n_array = jnp.stack(f_values)
        log_f_n = jnp.log(f_n_array + 1e-12)
        return theil_sen_slope(log_n, log_f_n)
        
    return kernel