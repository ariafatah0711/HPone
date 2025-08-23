"""
List helpers for HPone.

Functions to list honeypots and resolve honeypot directory IDs.
"""

import glob
from pathlib import Path
from typing import List

try:
    import yaml  # type: ignore
except ImportError:
    raise ImportError("PyYAML is required for this module")

# Import constants dari helpers
from core.constants import HONEYPOT_MANIFEST_DIR, OUTPUT_DOCKER_DIR
from core.utils import COLOR_GREEN, COLOR_RED, COLOR_CYAN, COLOR_GRAY, _format_table

# Import konfigurasi dari config.py
try:
    from config import LIST_BASIC_MAX_WIDTH, LIST_DETAILED_MAX_WIDTH, ALWAYS_IMPORT
except ImportError:
    # Fallback ke default values jika config.py tidak ditemukan
    LIST_BASIC_MAX_WIDTH = 60
    LIST_DETAILED_MAX_WIDTH = 30
    ALWAYS_IMPORT = True

def list_enabled_honeypot_ids() -> List[str]:
    honeypot_ids: List[str] = []
    for path_str in glob.glob(str(HONEYPOT_MANIFEST_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if data.get("enabled") is True:
                # Hanya anggap imported jika folder docker/<stem> ada
                if (OUTPUT_DOCKER_DIR / p.stem).exists():
                    honeypot_ids.append(p.stem)
        except Exception:
            continue
    return sorted(honeypot_ids)


def list_all_enabled_honeypot_ids() -> List[str]:
    """Return all enabled honeypot IDs (imported or not)."""
    honeypot_ids: List[str] = []
    for path_str in glob.glob(str(HONEYPOT_MANIFEST_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if data.get("enabled") is True:
                honeypot_ids.append(p.stem)
        except Exception:
            continue
    return sorted(honeypot_ids)


def list_imported_honeypot_ids() -> List[str]:
    result: List[str] = []
    if not OUTPUT_DOCKER_DIR.exists():
        return result
    for d in sorted(OUTPUT_DOCKER_DIR.iterdir()):
        if not d.is_dir():
            continue
        if (d / "docker-compose.yml").exists():
            result.append(d.name)
    return result


def resolve_honeypot_dir_id(honeypot_id: str) -> str:
    # Jika folder docker/<honeypot_id> ada, gunakan langsung
    if (OUTPUT_DOCKER_DIR / honeypot_id).exists():
        return honeypot_id
    # Coba stem dari YAML
    try:
        from core.yaml import find_honeypot_yaml_path
        yaml_path = find_honeypot_yaml_path(honeypot_id)
        candidate = Path(yaml_path).stem
        if (OUTPUT_DOCKER_DIR / candidate).exists():
            return candidate
    except FileNotFoundError:
        pass
    return honeypot_id


def list_honeypots(detailed: bool = False) -> None:
    """Print the list of honeypots in a clean table format."""
    yaml_files = sorted(glob.glob(str(HONEYPOT_MANIFEST_DIR / "*.yml")))
    if not yaml_files:
        print(f"No YAML files in the '{HONEYPOT_MANIFEST_DIR}' directory.")
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
        from core.docker import is_honeypot_running
        running_flag = is_honeypot_running(p.stem)

        # Apply ANSI colors using utils constants
        enabled_str = f"{COLOR_GREEN}True\033[0m" if enabled_flag else f"{COLOR_RED}False\033[0m"
        imported_str = f"{COLOR_CYAN}Yes\033[0m" if imported_flag else f"{COLOR_GRAY}No\033[0m"
        status_str = f"{COLOR_GREEN}Up\033[0m" if running_flag else f"{COLOR_RED}Down\033[0m"

        rows_basic.append([name, enabled_str, imported_str, status_str, description])

        if detailed:
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
        if ALWAYS_IMPORT:
            # Hide IMPORT column when ALWAYS_IMPORT=true
            table = _format_table(["HONEYPOT", "ENABLE", "STATUS", "DESCRIPTION", "PORTS", "VOLUMES"],
                                [[row[0], row[1], row[3], row[4], row[5], row[6]] for row in rows_detail],
                                max_width=LIST_DETAILED_MAX_WIDTH)
        else:
            table = _format_table(["HONEYPOT", "ENABLE", "IMPORT", "STATUS", "DESCRIPTION", "PORTS", "VOLUMES"], rows_detail, max_width=LIST_DETAILED_MAX_WIDTH)
    else:
        if ALWAYS_IMPORT:
            # Hide IMPORT column when ALWAYS_IMPORT=true
            table = _format_table(["HONEYPOT", "ENABLE", "STATUS", "DESCRIPTION"],
                                [[row[0], row[1], row[3], row[4]] for row in rows_basic],
                                max_width=LIST_BASIC_MAX_WIDTH)
        else:
            table = _format_table(["HONEYPOT", "ENABLE", "IMPORT", "STATUS", "DESCRIPTION"], rows_basic, max_width=LIST_BASIC_MAX_WIDTH)

    print(table)
