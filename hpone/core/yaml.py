"""
YAML helpers for HPone.

Functions to read, write, and manipulate tool YAML files.
"""

import glob
from pathlib import Path
from typing import Dict, Any, Tuple

try:
    import yaml  # type: ignore
except ImportError:
    raise ImportError("PyYAML is required for this module")

# Import constants dari helpers
from .constants import TOOLS_DIR

def load_tool_yaml_by_filename(tool_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Read YAML `tools/<tool_id>.yml`. If it does not exist, search YAML files that have `name: <tool_id>` (case-insensitive).
    Return (resolved_tool_name, config_dict).
    """
    explicit_path = TOOLS_DIR / f"{tool_id}.yml"
    if explicit_path.exists():
        with explicit_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        resolved_name = str(data.get("name") or tool_id)
        return resolved_name, data

    # Fallback: search by `name` field
    for path_str in glob.glob(str(TOOLS_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if str(data.get("name", "")).lower() == tool_id.lower():
                return str(data.get("name")), data
        except Exception:
            continue

    raise FileNotFoundError(f"Config YAML for tool '{tool_id}' not found in '{TOOLS_DIR}'.")


def find_tool_yaml_path(tool_id: str) -> Path:
    """Return YAML path for tool_id by filename or `name` field inside YAML."""
    explicit_path = TOOLS_DIR / f"{tool_id}.yml"
    if explicit_path.exists():
        return explicit_path
    for path_str in glob.glob(str(TOOLS_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if str(data.get("name", "")).lower() == tool_id.lower():
                return p
        except Exception:
            continue
    raise FileNotFoundError(f"YAML file for tool '{tool_id}' not found in '{TOOLS_DIR}'.")


def set_tool_enabled(tool_id: str, enabled: bool) -> None:
    """Set `enabled` field in `tools/<tool>.yml`. Matches by filename or `name` field."""
    yaml_path = find_tool_yaml_path(tool_id)
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data["enabled"] = bool(enabled)
    with yaml_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def is_tool_enabled(tool_id: str) -> bool:
    try:
        yaml_path = find_tool_yaml_path(tool_id)
    except FileNotFoundError:
        return False
    try:
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return bool(data.get("enabled") is True)
    except Exception:
        return False
