import gc
import jax

def force_clear_memory():
    for _ in range(3):
        gc.collect()
    jax.clear_caches()