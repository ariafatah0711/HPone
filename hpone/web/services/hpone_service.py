from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple
import subprocess

import yaml

from core.constants import HONEYPOT_MANIFEST_DIR, OUTPUT_DOCKER_DIR
from core.yaml import (
    load_honeypot_yaml_by_filename,
    find_honeypot_yaml_path,
    set_honeypot_enabled,
    is_honeypot_enabled,
)
from core.config import parse_ports, parse_volumes
from core.docker import is_honeypot_running, up_honeypot, down_honeypot
from scripts.import_cmd import import_honeypot

try:
    from config import ALWAYS_IMPORT
except ImportError:
    ALWAYS_IMPORT = True


@dataclass(frozen=True)
class HoneypotSummary:
    honeypot_id: str
    name: str
    description: str
    enabled: bool
    imported: bool
    running: bool
    ports: List[Tuple[str, str]]
    volumes: List[Tuple[str, str]]
    yaml_path: Path

class HoneypotNotFound(Exception):
    pass

def _all_yaml_paths() -> List[Path]:
    return sorted(HONEYPOT_MANIFEST_DIR.glob("*.yml"))

def list_honeypots() -> List[HoneypotSummary]:
    honeypots: List[HoneypotSummary] = []
    for yaml_path in _all_yaml_paths():
        data = _read_yaml_safe(yaml_path)
        honeypot_id = yaml_path.stem
        name = str(data.get("name") or honeypot_id)
        description = str(data.get("description") or "")
        enabled = bool(data.get("enabled") is True)
        imported = (OUTPUT_DOCKER_DIR / honeypot_id).exists()
        running = is_honeypot_running(honeypot_id)
        ports = _safe_ports(data)
        volumes = _safe_volumes(data)
        honeypots.append(
            HoneypotSummary(
                honeypot_id=honeypot_id,
                name=name,
                description=description,
                enabled=enabled,
                imported=imported,
                running=running,
                ports=ports,
                volumes=volumes,
                yaml_path=yaml_path,
            )
        )
    return honeypots


def get_honeypot_detail(honeypot_id: str) -> Dict[str, Any]:
    resolved_name, config = load_honeypot_yaml_by_filename(honeypot_id)
    yaml_path = find_honeypot_yaml_path(honeypot_id)
    imported = (OUTPUT_DOCKER_DIR / yaml_path.stem).exists()
    return {
        "honeypot_id": yaml_path.stem,
        "name": resolved_name,
        "config": config,
        "enabled": is_honeypot_enabled(honeypot_id),
        "imported": imported,
        "running": is_honeypot_running(honeypot_id),
        "ports": _safe_ports(config),
        "volumes": _safe_volumes(config),
        "yaml_path": yaml_path,
    }


def enable_honeypot(honeypot_id: str, enabled: bool) -> None:
    _ensure_exists(honeypot_id)
    set_honeypot_enabled(honeypot_id, enabled)


def start_honeypot(honeypot_id: str, force: bool = False) -> None:
    _ensure_exists(honeypot_id)
    if ALWAYS_IMPORT:
        import_honeypot(honeypot_id, force=True)
    up_honeypot(honeypot_id, force=force)


def stop_honeypot(honeypot_id: str) -> None:
    _ensure_exists(honeypot_id)
    down_honeypot(honeypot_id)


def read_yaml_text(honeypot_id: str) -> str:
    yaml_path = find_honeypot_yaml_path(honeypot_id)
    return yaml_path.read_text(encoding="utf-8")


def write_yaml_text(honeypot_id: str, content: str) -> None:
    yaml_path = find_honeypot_yaml_path(honeypot_id)
    _validate_yaml_content(content)
    yaml_path.write_text(content, encoding="utf-8")


def get_logs(honeypot_id: str, lines: int = 200) -> str:
    _ensure_exists(honeypot_id)
    cmd = ["docker", "logs", "--tail", str(lines), honeypot_id]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        output = result.stdout or ""
        if result.stderr:
            output += "\n" + result.stderr
        return output.strip()
    except FileNotFoundError:
        return "Docker is not installed or not in PATH."


def _ensure_exists(honeypot_id: str) -> None:
    try:
        find_honeypot_yaml_path(honeypot_id)
    except FileNotFoundError as exc:
        raise HoneypotNotFound(str(exc)) from exc


def _read_yaml_safe(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except Exception:
        return {}


def _validate_yaml_content(content: str) -> None:
    try:
        yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from exc


def _safe_ports(config: Dict[str, Any]) -> List[Tuple[str, str]]:
    try:
        return parse_ports(config)
    except Exception:
        return []


def _safe_volumes(config: Dict[str, Any]) -> List[Tuple[str, str]]:
    try:
        return parse_volumes(config)
    except Exception:
        return []
