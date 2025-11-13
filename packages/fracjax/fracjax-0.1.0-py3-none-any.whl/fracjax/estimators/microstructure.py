import jax
import jax.numpy as jnp

def cvd_proxy_kernel(window_ohlcv: jnp.ndarray) -> jnp.ndarray:
    O = window_ohlcv[:, 0]
    H = window_ohlcv[:, 1]
    L = window_ohlcv[:, 2]
    C = window_ohlcv[:, 3]
    V = window_ohlcv[:, 4]

    range_hl = jnp.maximum(H - L, 1e-8)
    price_pos = (C - O) / range_hl
    buy_ratio = (price_pos + 1.0) / 2.0
    buy_vol = V * buy_ratio
    sell_vol = V * (1.0 - buy_ratio)
    
    delta = buy_vol - sell_vol
    return jnp.sum(delta)

def amihud_illiquidity_kernel(window_ohlcv: jnp.ndarray) -> jnp.ndarray:
    C = window_ohlcv[:, 3]
    V = window_ohlcv[:, 4]
    
    ret = jnp.abs(jnp.diff(C, prepend=C[0]))
    dollar_vol = C * V
    dollar_vol = jnp.maximum(dollar_vol, 1.0)
    
    ratio = ret / dollar_vol
    return jnp.mean(ratio) * 1e6

def make_kernel(mode: str):
    if mode == 'cvd':
        return cvd_proxy_kernel
    elif mode == 'amihud':
        return amihud_illiquidity_kernel
    else:
        raise ValueError(f"Unknown microstructure mode: {mode}")