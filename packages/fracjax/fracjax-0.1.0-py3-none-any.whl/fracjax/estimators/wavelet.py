import jax.numpy as jnp
import jax
from ..math.regression import theil_sen_slope
from ..math.transforms import dwt_one_level

def make_kernel(max_level: int = 4):
    def kernel(window_data: jnp.ndarray) -> jnp.ndarray:
        profile = jnp.cumsum(window_data - jnp.mean(window_data))
        log_scales = []
        log_energies = []
        current_app = profile
        
        for level in range(1, max_level + 1):
            current_app, detail = dwt_one_level(current_app)
            energy = jnp.mean(detail ** 2)
            log_scales.append(jnp.log(2.0 ** level))
            log_energies.append(jnp.log(energy + 1e-12))
            
        x = jnp.array(log_scales)
        y = jnp.array(log_energies)
        
        slope = theil_sen_slope(x, y)
        return (slope - 1.0) / 2.0
        
    return kernel