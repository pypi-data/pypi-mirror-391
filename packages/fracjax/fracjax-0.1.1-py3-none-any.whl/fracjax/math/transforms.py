import jax
import jax.numpy as jnp
from typing import Tuple

DB2_LOW = jnp.array([0.48296291, 0.83651630, 0.22414387, -0.12940952], dtype=jnp.float32)
DB2_HIGH = jnp.array([-0.12940952, -0.22414387, 0.83651630, -0.48296291], dtype=jnp.float32)

@jax.jit
def dwt_one_level(signal: jnp.ndarray) -> Tuple[jnp.ndarray, jnp.ndarray]:
    x = signal[None, :, None]
    f_low = DB2_LOW[:, None, None]
    f_high = DB2_HIGH[:, None, None]
    
    low = jax.lax.conv_general_dilated(
        x, f_low, window_strides=(2,), padding='VALID', 
        dimension_numbers=('NHC', 'HIO', 'NHC')
    )
    high = jax.lax.conv_general_dilated(
        x, f_high, window_strides=(2,), padding='VALID', 
        dimension_numbers=('NHC', 'HIO', 'NHC')
    )
    return low.squeeze(), high.squeeze()