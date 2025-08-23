"""
Status helpers for HPone.

Provides a consolidated status output that shows:
- Services table: HONEYPOT | ENABLED | STATUS (Up/Down)
- Ports table: HOST | CONTAINER | SERVICE (for running honeypots)
"""

from typing import List
import glob
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

from core.constants import HONEYPOT_MANIFEST_DIR, OUTPUT_DOCKER_DIR
from core.utils import _format_table, COLOR_GREEN, COLOR_RED, COLOR_CYAN
from core.docker import is_honeypot_running
from core.yaml import load_honeypot_yaml_by_filename
from core.config import parse_ports

def _color(text: str, code: str) -> str:
    # Backward-compatible wrapper if other parts still pass numeric codes
    if code == "32":
        return f"{COLOR_GREEN}{text}\033[0m"
    if code == "31":
        return f"{COLOR_RED}{text}\033[0m"
    if code == "36":
        return f"{COLOR_CYAN}{text}\033[0m"
    return text

def _gather_services_status() -> List[List[str]]:
    rows: List[List[str]] = []
    for path_str in sorted(glob.glob(str(HONEYPOT_MANIFEST_DIR / "*.yml"))):
        p = Path(path_str)
        honeypot_id = p.stem
        enabled_flag = False
        try:
            if yaml is None:
                data = {}
            else:
                with p.open("r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            enabled_flag = bool(data.get("enabled") is True)
        except Exception:
            data = {}

        running_flag = is_honeypot_running(honeypot_id)
        name = str(data.get("name") or honeypot_id)
        enabled_str = _color("True", "32") if enabled_flag else _color("False", "31")
        status_str = _color("Up", "32") if running_flag else _color("Down", "31")
        rows.append([name, enabled_str, status_str])

    return rows


def _gather_ports_rows(running_honeypots: List[str]) -> List[List[str]]:
    rows: List[List[str]] = []
    for t in running_honeypots:
        try:
            _resolved_name, cfg = load_honeypot_yaml_by_filename(t)
            port_pairs = parse_ports(cfg)
        except Exception:
            port_pairs = []

        for host, container in port_pairs:
            container_str = str(container)
            lc = container_str.lower()
            if ("/udp" not in lc) and ("/tcp" not in lc):
                container_str = f"{container_str}/tcp"
            rows.append([str(host), container_str, t])
    # Sort by HOST numerically if possible
    def _key_host(row):
        try:
            return int(str(row[0]).split("/")[0])
        except Exception:
            return str(row[0])
    rows.sort(key=_key_host)
    return rows

def show_status() -> None:
    # Services table
    # svc_rows = _gather_services_status()
    # svc_table = _format_table(["HONEYPOT", "ENABLED", "STATUS"], svc_rows, max_width=30)
    # if svc_table:
    #     print(svc_table)

    # Ports table: only for running honeypots present under docker/
    running_honeypots: List[str] = []
    if OUTPUT_DOCKER_DIR.exists():
        for d in sorted(OUTPUT_DOCKER_DIR.iterdir()):
            if d.is_dir() and (d / "docker-compose.yml").exists():
                honeypot_id = d.name
                if is_honeypot_running(honeypot_id):
                    running_honeypots.append(honeypot_id)

    port_rows = _gather_ports_rows(running_honeypots)
    if port_rows:
        # Colorize service name in ports table for readability
        colored_rows = []
        for host, container, svc in port_rows:
            colored_rows.append([host, container, _color(svc, "36")])
        port_table = _format_table(["HOST", "CONTAINER", "SERVICE"], colored_rows, max_width=30)
        if port_table:
            print(port_table)
