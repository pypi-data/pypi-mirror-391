import jax
import jax.numpy as jnp
from jax.scipy.special import logsumexp
from ..math.regression import theil_sen_slope

def cointegration_zscore_kernel(window_pair: jnp.ndarray) -> jnp.ndarray:
    
    y = window_pair[:, 0]
    x = window_pair[:, 1]
    
    beta = theil_sen_slope(x, y)
    spread = y - beta * x
    
    mean_spr = jnp.mean(spread)
    std_spr = jnp.std(spread)
    
    return (spread[-1] - mean_spr) / (std_spr + 1e-12)

def _gaussian_entropy(data: jnp.ndarray, sigma: float = 1.0) -> jnp.ndarray:
    
    n = data.shape[0]
    
    h = 1.06 * sigma * (n ** (-0.2))
    
    
    diffs = data[:, None] - data[None, :]
    squared_dists = diffs ** 2
    
   
    log_probs = logsumexp(-0.5 * squared_dists / (h**2), axis=1) - jnp.log(n * h * jnp.sqrt(2 * jnp.pi))
    
    return -jnp.mean(log_probs)

def _joint_gaussian_entropy(x: jnp.ndarray, y: jnp.ndarray) -> jnp.ndarray:

    data = jnp.stack([x, y], axis=1) 
    n, d = data.shape
    
    h = 1.06 * (n ** (-1.0 / (d + 4)))
    
    diffs = data[:, None, :] - data[None, :, :]
    squared_dists = jnp.sum(diffs ** 2, axis=-1)
    
    log_probs = logsumexp(-0.5 * squared_dists / (h**2), axis=1) - jnp.log(n * (h**d) * ((2 * jnp.pi)**(d/2)))
    return -jnp.mean(log_probs)

def lead_lag_mi_kernel(window_pair: jnp.ndarray, lag: int = 1) -> jnp.ndarray:
    
    x = window_pair[:, 0] 
    y = window_pair[:, 1] 
    
    x_c = x[lag:]
    y_lag = y[:-lag]
    
    x_std = (x_c - jnp.mean(x_c)) / (jnp.std(x_c) + 1e-9)
    y_std = (y_lag - jnp.mean(y_lag)) / (jnp.std(y_lag) + 1e-9)
    
    h_x = _gaussian_entropy(x_std)
    h_y = _gaussian_entropy(y_std)
    h_xy = _joint_gaussian_entropy(x_std, y_std)
    
    mi = h_x + h_y - h_xy
    return jnp.maximum(mi, 0.0)

def make_kernel(mode: str = 'coint', **kwargs):
    if mode == 'coint':
        return cointegration_zscore_kernel
    
    elif mode == 'lead_lag':
        lag = kwargs.get('lag', 1)
        def kernel(window: jnp.ndarray) -> jnp.ndarray:
            return lead_lag_mi_kernel(window, lag=lag)
        return kernel
        
    else:
        raise ValueError(f"Unknown intermarket mode: {mode}")