import jax
import jax.numpy as jnp

def garch_forecast_kernel(window_returns: jnp.ndarray, omega: float = 1e-6, alpha: float = 0.09, beta: float = 0.90) -> jnp.ndarray:
    def step(var_t, ret_t):
        var_next = omega + alpha * (ret_t ** 2) + beta * var_t
        return var_next, var_next

    init_var = jnp.var(window_returns)
    _, var_path = jax.lax.scan(step, init_var, window_returns)
    return jnp.sqrt(var_path[-1])

def realized_semivariance_kernel(window_returns: jnp.ndarray) -> jnp.ndarray:
    negative_returns = jnp.minimum(window_returns, 0.0)
    return jnp.sum(negative_returns ** 2)

def make_kernel(mode: str):
    if mode == 'garch':
        def kernel(window: jnp.ndarray) -> jnp.ndarray:
            return garch_forecast_kernel(window)
        return kernel
    elif mode == 'semivariance':
        def kernel(window: jnp.ndarray) -> jnp.ndarray:
            return realized_semivariance_kernel(window)
        return kernel
    else:
        raise ValueError(f"Unknown volatility mode: {mode}")