# src/code_analyzer/config/loader.py
import yaml
import json
from pathlib import Path
from copy import deepcopy

DEFAULT_DIR = Path(__file__).parent / "defaults"


def deep_merge(a: dict, b: dict) -> dict:
    out = deepcopy(a)
    for k, v in (b or {}).items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = deepcopy(v)
    return out


def load_config(explicit_path: str = None) -> dict:
    """
    Load config for language with precedence:
      1) explicit path
      2) ./ .codecomplex/<language>.yaml
      3) ~/.config/codecomplex/<language>.yaml
      4) package defaults (config/defaults/<language>.yaml)
    Returns merged dict (defaults overwritten by higher precedence).
    """
    candidates = []
    if explicit_path:
        candidates.append(Path(explicit_path))
    config_file_name = "config.yaml"
    candidates.append(Path(".") / ".code_analyzer" / f"{config_file_name}")
    candidates.append(Path.home() / ".config" / "code_analyzer" / f"{config_file_name}")
    candidates.append(DEFAULT_DIR / f"{config_file_name}")

    merged = {}
    for p in candidates:
        if p and p.exists():
            text = p.read_text(encoding="utf-8")
            if p.suffix.lower() in (".yaml", ".yml"):
                cfg = yaml.safe_load(text) or {}
            elif p.suffix.lower() == ".json":
                cfg = json.loads(text) or {}
            else:
                cfg = yaml.safe_load(text) or {}
            merged = deep_merge(merged, cfg)
    
    return merged
