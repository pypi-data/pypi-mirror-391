import json
from pathlib import Path
import pandas as pd
import numpy as np
import sys
import platform
import jax

def save_parquet_with_metadata(df: pd.DataFrame, path: str, metadata: dict):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(p)
    meta_path = p.with_suffix(p.suffix + ".meta.json")
    meta = dict(metadata)
    try:
        meta["_env"] = {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "jax": getattr(jax, "__version__", None)
        }
    except Exception:
        meta["_env"] = {}
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return str(p), str(meta_path)