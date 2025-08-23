"""
YAML helpers for HPone.

Functions to read, write, and manipulate honeypot YAML files.
"""

import glob
from pathlib import Path
from typing import Dict, Any, Tuple

try:
    import yaml  # type: ignore
except ImportError:
    raise ImportError("PyYAML is required for this module")

# Import constants dari helpers
from .constants import HONEYPOT_MANIFEST_DIR

def load_honeypot_yaml_by_filename(honeypot_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Read YAML `honeypots/<honeypot_id>.yml`. If it does not exist, search YAML files that have `name: <honeypot_id>` (case-insensitive).
    Return (resolved_honeypot_name, config_dict).
    """
    explicit_path = HONEYPOT_MANIFEST_DIR / f"{honeypot_id}.yml"
    if explicit_path.exists():
        with explicit_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        resolved_name = str(data.get("name") or honeypot_id)
        return resolved_name, data

    # Fallback: search by `name` field
    for path_str in glob.glob(str(HONEYPOT_MANIFEST_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if str(data.get("name", "")).lower() == honeypot_id.lower():
                return str(data.get("name")), data
        except Exception:
            continue

    raise FileNotFoundError(f"Config YAML for honeypot '{honeypot_id}' not found in '{HONEYPOT_MANIFEST_DIR}'.")


def find_honeypot_yaml_path(honeypot_id: str) -> Path:
    """Return YAML path for honeypot_id by filename or `name` field inside YAML."""
    explicit_path = HONEYPOT_MANIFEST_DIR / f"{honeypot_id}.yml"
    if explicit_path.exists():
        return explicit_path
    for path_str in glob.glob(str(HONEYPOT_MANIFEST_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if str(data.get("name", "")).lower() == honeypot_id.lower():
                return p
        except Exception:
            continue
    raise FileNotFoundError(f"YAML file for honeypot '{honeypot_id}' not found in '{HONEYPOT_MANIFEST_DIR}'.")


def set_honeypot_enabled(honeypot_id: str, enabled: bool) -> None:
    """Set `enabled` field in `honeypots/<honeypot>.yml`. Matches by filename or `name` field."""
    yaml_path = find_honeypot_yaml_path(honeypot_id)
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data["enabled"] = bool(enabled)
    with yaml_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def is_honeypot_enabled(honeypot_id: str) -> bool:
    try:
        yaml_path = find_honeypot_yaml_path(honeypot_id)
    except FileNotFoundError:
        return False
    try:
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return bool(data.get("enabled") is True)
    except Exception:
        return False


def get_custom_template_dir(honeypot_id: str) -> Path | None:
    """
    Get custom template directory from honeypot YAML config.
    Returns None if no custom template_dir is specified.
    """
    try:
        yaml_path = find_honeypot_yaml_path(honeypot_id)
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        template_dir = data.get("template_dir")
        if template_dir:
            # Convert to Path and resolve relative paths
            custom_path = Path(template_dir)
            if not custom_path.is_absolute():
                # Resolve relative to the project root or YAML location
                from .constants import PROJECT_ROOT
                custom_path = PROJECT_ROOT / custom_path
            return custom_path
        return None
    except Exception:
        return None
