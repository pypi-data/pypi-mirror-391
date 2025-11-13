import jax
import jax.numpy as jnp
from jax.lax import dynamic_slice
import math

def permutation_entropy_kernel(window_data: jnp.ndarray, m: int = 3, delay: int = 1) -> jnp.ndarray:
    n = window_data.shape[0]
    num_patterns = n - (m - 1) * delay
    
    indices = jnp.arange(num_patterns)
    
    def get_pattern(i):
        sl = dynamic_slice(window_data, (i,), (m * delay,))
        return sl[::delay]
        
    patterns = jax.vmap(get_pattern)(indices)
    perms = jnp.argsort(patterns, axis=1)
    
    base = jnp.power(m, jnp.arange(m))
    hashes = jnp.sum(perms * base, axis=1)
    
    counts = jnp.bincount(hashes, length=m**m + 1)
    probs = counts / num_patterns
    
    safe_probs = jnp.where(probs > 0, probs, 1.0)
    
    pe = -jnp.sum(probs * jnp.log(safe_probs))
    
    return pe / jnp.log(float(math.factorial(m)))

def hill_estimator_kernel(window_returns: jnp.ndarray, tail_fraction: float = 0.05) -> jnp.ndarray:
    abs_ret = jnp.abs(window_returns)
    
    n = window_returns.shape[0]
    k = int(n * tail_fraction)
    k = max(2, k)
    
    sorted_ret = jnp.sort(abs_ret)
    
    tail = sorted_ret[-k:]
    min_tail = tail[0]
    
    hill = jnp.mean(jnp.log(tail / (min_tail + 1e-12)))
    return 1.0 / (hill + 1e-12)

def make_kernel(mode: str, **kwargs):
    if mode == 'permutation':
        m = kwargs.get('m', 3)
        delay = kwargs.get('delay', 1)
        def kernel(window: jnp.ndarray) -> jnp.ndarray:
            return permutation_entropy_kernel(window, m, delay)
        return kernel
    elif mode == 'hill':
        tail_frac = kwargs.get('tail_fraction', 0.05)
        def kernel(window: jnp.ndarray) -> jnp.ndarray:
            return hill_estimator_kernel(window, tail_frac)
        return kernel
    else:
        raise ValueError(f"Unknown entropy mode: {mode}")