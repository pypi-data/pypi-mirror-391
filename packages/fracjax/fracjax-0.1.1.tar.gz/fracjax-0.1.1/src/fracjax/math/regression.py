import jax
import jax.numpy as jnp

@jax.jit
def theil_sen_slope(x: jnp.ndarray, y: jnp.ndarray) -> jnp.ndarray:
    n = x.shape[0]
    idx_i, idx_j = jnp.triu_indices(n, k=1)
    dx = x[idx_j] - x[idx_i]
    dy = y[idx_j] - y[idx_i]
    valid = dx != 0.0
    slopes = jnp.where(valid, dy / (dx + 1e-12), jnp.nan)
    return jnp.nanmedian(slopes)