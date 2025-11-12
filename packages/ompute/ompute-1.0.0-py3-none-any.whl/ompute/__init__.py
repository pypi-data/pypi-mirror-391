from __future__ import annotations
import os
import sys
import subprocess
from typing import Optional, Any, Callable, Dict, List

_MODEL_NAMES: List[str] = [
    "aenc","bayreg","enet","expmax","hotdeck","knn","lls",
    "mean","median","mice","mindet","minprob","missforest",
    "missmda","mode","pdn","ppca","qrilc","rnf","sfi",
    "svd","tni","trb1","trb2","trb3","trb4","trb5","trb6",
    "trb7","trb8","trb9","trb10"
]

def _script_path(name: str) -> str:
    base = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(base, "model", f"{name}.py"))

def _format_extra_args(kwargs: Dict[str, Any]) -> List[str]:
    args: List[str] = []
    for k, v in kwargs.items():
        if v is None:
            continue
        flag = f"--{k}"
        if isinstance(v, bool):
            if v:
                args.append(flag)
        elif isinstance(v, (list, tuple)):
            for item in v:
                args.append(flag); args.append(str(item))
        else:
            args.append(flag); args.append(str(v))
    return args

def _run_model(name: str, i: str, d: str, o: str, *, return_df: bool = False, timeout: Optional[float] = None, **kwargs) -> Optional[Any]:
    model_file = _script_path(name)
    if not os.path.isfile(model_file):
        raise FileNotFoundError(model_file)
    python_exec = sys.executable or "python"
    cmd = [python_exec, model_file, "--i", i, "--d", d, "--o", o]
    cmd.extend(_format_extra_args(kwargs))
    outdir = os.path.dirname(o) or "."
    os.makedirs(outdir, exist_ok=True)
    try:
        completed = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.CalledProcessError as e:
        msg = f"Model script '{name}' failed with exit code {e.returncode}.\ncmd: {' '.join(map(str,e.cmd))}\n--- stdout ---\n{e.stdout}\n--- stderr ---\n{e.stderr}\n"
        raise RuntimeError(msg) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Model script '{name}' timed out after {timeout} seconds.") from e
    if return_df:
        try:
            import pandas as pd
        except Exception as e:
            raise RuntimeError("pandas is required for return_df=True.") from e
        if not os.path.isfile(o):
            raise FileNotFoundError(o)
        return pd.read_csv(o)
    return None

def _make_wrapper(name: str) -> Callable[..., Optional[Any]]:
    def wrapper(i: str, d: str, o: str, *, return_df: bool = False, timeout: Optional[float] = None, **kwargs):
        return _run_model(name, i=i, d=d, o=o, return_df=return_df, timeout=timeout, **kwargs)
    wrapper.__name__ = name
    return wrapper

for _name in _MODEL_NAMES:
    globals()[_name] = _make_wrapper(_name)

__all__ = _MODEL_NAMES[:]

