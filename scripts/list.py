"""
List helpers for HPone.

Functions to list tools and resolve tool directory IDs.
"""

import glob
from pathlib import Path
from typing import List

try:
    import yaml  # type: ignore
except ImportError:
    raise ImportError("PyYAML is required for this module")

# Import constants dari helpers
from core.constants import TOOLS_DIR, OUTPUT_DOCKER_DIR

def list_enabled_tool_ids() -> List[str]:
    tool_ids: List[str] = []
    for path_str in glob.glob(str(TOOLS_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if data.get("enabled") is True:
                # Hanya anggap imported jika folder docker/<stem> ada
                if (OUTPUT_DOCKER_DIR / p.stem).exists():
                    tool_ids.append(p.stem)
        except Exception:
            continue
    return sorted(tool_ids)


def list_all_enabled_tool_ids() -> List[str]:
    """Return all enabled tool IDs (imported or not)."""
    tool_ids: List[str] = []
    for path_str in glob.glob(str(TOOLS_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if data.get("enabled") is True:
                tool_ids.append(p.stem)
        except Exception:
            continue
    return sorted(tool_ids)


def list_imported_tool_ids() -> List[str]:
    result: List[str] = []
    if not OUTPUT_DOCKER_DIR.exists():
        return result
    for d in sorted(OUTPUT_DOCKER_DIR.iterdir()):
        if not d.is_dir():
            continue
        if (d / "docker-compose.yml").exists():
            result.append(d.name)
    return result


def resolve_tool_dir_id(tool_id: str) -> str:
    # Jika folder docker/<tool_id> ada, gunakan langsung
    if (OUTPUT_DOCKER_DIR / tool_id).exists():
        return tool_id
    # Coba stem dari YAML
    try:
        from core.yaml import find_tool_yaml_path
        yaml_path = find_tool_yaml_path(tool_id)
        candidate = Path(yaml_path).stem
        if (OUTPUT_DOCKER_DIR / candidate).exists():
            return candidate
    except FileNotFoundError:
        pass
    return tool_id


def list_tools(detailed: bool = False) -> None:
    """Print the list of tools in a clean table format."""
    yaml_files = sorted(glob.glob(str(TOOLS_DIR / "*.yml")))
    if not yaml_files:
        print("No YAML files in the 'tools/' directory.")
        return

    rows_basic: List[List[str]] = []
    rows_detail: List[List[str]] = []

    for path_str in yaml_files:
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            data = {}

        name = str(data.get("name") or p.stem)
        description = str(data.get("description") or "")
        enabled_flag = bool(data.get("enabled") is True)
        imported_flag = (OUTPUT_DOCKER_DIR / p.stem).exists()
        
        # Import di dalam function untuk avoid circular import
        from core.docker import is_tool_running
        running_flag = is_tool_running(p.stem)

        # Apply ANSI colors for readability
        def color(text: str, code: str) -> str:
            return f"\033[{code}m{text}\033[0m"

        enabled_str = color("True", "32") if enabled_flag else color("False", "31")
        imported_str = color("Yes", "36") if imported_flag else color("No", "90")
        status_str = color("Up", "32") if running_flag else color("Down", "31")

        rows_basic.append([name, enabled_str, imported_str, status_str, description])

        if detailed:
            # Ports
            ports_info = ""
            try:
                from core.config import parse_ports
                ports = parse_ports(data)
                if ports:
                    ports_info = ", ".join([f"{host}:{container}" for host, container in ports])
            except Exception:
                ports_info = "(error parsing)"
            # Volumes
            volumes_info = ""
            try:
                from core.config import parse_volumes
                vols = parse_volumes(data)
                if vols:
                    volumes_info = ", ".join([f"{src}:{dst}" for src, dst in vols])
            except Exception:
                volumes_info = "(error parsing)"

            rows_detail.append([name, enabled_str, imported_str, status_str, description, ports_info, volumes_info])

    if detailed:
        from core.utils import _format_table
        table = _format_table(["TOOL", "ENABLE", "IMPORT", "STATUS", "DESCRIPTION", "PORTS", "VOLUMES"], rows_detail, max_width=30)
    else:
        from core.utils import _format_table
        table = _format_table(["TOOL", "ENABLE", "IMPORT", "STATUS", "DESCRIPTION"], rows_basic, max_width=60)

    print(table)
