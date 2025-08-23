"""
Config helpers for HPone.

Functions to parse ports, volumes, environment variables, and generate config files.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    import yaml  # type: ignore
except ImportError:
    raise ImportError("PyYAML is required for this module")

# Import constants dan functions dari helpers
from .constants import PROJECT_ROOT
from .utils import to_var_prefix


def parse_ports(config: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Return list of (host_src, container_dst). Supports dict or 'host:container' string."""
    result: List[Tuple[str, str]] = []
    ports = config.get("ports") or []
    for entry in ports:
        if isinstance(entry, dict):
            # Support keys 'host'/'container' or 'src'/'dst'
            host = entry.get("host") or entry.get("src") or entry.get("source")
            container = entry.get("container") or entry.get("dst") or entry.get("destination")
            if host is not None and container is not None:
                result.append((str(host), str(container)))
                continue
        if isinstance(entry, str):
            # Format "2222:22" → take the first left and right parts
            if ":" in entry:
                left, right = entry.split(":", 1)
                result.append((left.strip(), right.strip()))
                continue
        raise ValueError(f"Unrecognized port format: {entry!r}")
    return result


def parse_ports_with_description(config: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Return list of (host_src, container_dst, description). Supports dict with optional description."""
    result: List[Tuple[str, str, str]] = []
    ports = config.get("ports") or []
    for entry in ports:
        if isinstance(entry, dict):
            # Support keys 'host'/'container' or 'src'/'dst'
            host = entry.get("host") or entry.get("src") or entry.get("source")
            container = entry.get("container") or entry.get("dst") or entry.get("destination")
            description = entry.get("description", "")
            if host is not None and container is not None:
                result.append((str(host), str(container), str(description)))
                continue
        if isinstance(entry, str):
            # Format "2222:22" → take the first left and right parts
            if ":" in entry:
                left, right = entry.split(":", 1)
                result.append((left.strip(), right.strip(), ""))
                continue
        raise ValueError(f"Unrecognized port format: {entry!r}")
    return result


def parse_volumes(config: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Return list of (src, dst). Supports 'src:dst' string or dict {'src'/'dst'} or {'host'/'container'}."""
    result: List[Tuple[str, str]] = []
    volumes = config.get("volumes") or []
    for entry in volumes:
        if isinstance(entry, dict):
            src = entry.get("src") or entry.get("source") or entry.get("host")
            dst = entry.get("dst") or entry.get("destination") or entry.get("container")
            if src is not None and dst is not None:
                result.append((str(src), str(dst)))
                continue
        if isinstance(entry, str):
            if ":" in entry:
                # Take the first two parts as src and dst (ignore extra modes like :ro)
                left, right = entry.split(":", 1)
                # If there is another ":" on the right (e.g. dst:ro), take only the destination path before the mode
                if ":" in right:
                    dst_path, _mode = right.split(":", 1)
                    result.append((left.strip(), dst_path.strip()))
                else:
                    result.append((left.strip(), right.strip()))
                continue
        raise ValueError(f"Unrecognized volume format: {entry!r}")
    return result


def parse_env(config: Dict[str, Any]) -> Dict[str, str]:
    env_mapping: Dict[str, str] = {}
    env = config.get("env") or {}
    if isinstance(env, dict):
        for k, v in env.items():
            env_mapping[str(k)] = "" if v is None else str(v)
    else:
        raise ValueError("Field 'env' must be a mapping/dict if present.")
    return env_mapping


def normalize_host_path(path_str: str) -> str:
    """Normalize host path for volumes:
    - Expand env vars (e.g., $HOME) and ~
    - If relative, make it absolute relative to the project root
    """
    if not isinstance(path_str, str) or not path_str:
        return path_str
    # Expand env vars and ~
    expanded = os.path.expandvars(os.path.expanduser(path_str))
    # If still relative, make absolute relative to the project root
    if not os.path.isabs(expanded):
        try:
            absolute = str((PROJECT_ROOT / expanded).resolve())
        except Exception:
            absolute = str(PROJECT_ROOT / expanded)
        return absolute
    return expanded


def generate_env_file(dest_dir: Path, honeypot_name: str, config: Dict[str, Any]) -> None:
    """Create a `.env` file in the destination directory based on YAML config."""
    prefix = to_var_prefix(honeypot_name)

    lines: List[str] = []
    lines.append(f"# Auto-generated by manage.py for {honeypot_name}")

    # Ports
    try:
        port_mappings = parse_ports(config)
    except Exception as exc:
        raise ValueError(f"Failed parsing 'ports': {exc}")

    for idx, (host_src, container_dst) in enumerate(port_mappings, start=1):
        lines.append(f"{prefix}_PORT{idx}_SRC={host_src}")
        lines.append(f"{prefix}_PORT{idx}_DST={container_dst}")

    # Volumes
    try:
        volume_mappings = parse_volumes(config)
    except Exception as exc:
        raise ValueError(f"Failed parsing 'volumes': {exc}")

    for idx, (src, dst) in enumerate(volume_mappings, start=1):
        normalized_src = normalize_host_path(src)
        lines.append(f"{prefix}_VOL{idx}_SRC={normalized_src}")
        lines.append(f"{prefix}_VOL{idx}_DST={dst}")

    # Env
    env_mapping = parse_env(config)
    for k, v in env_mapping.items():
        key_name = re.sub(r"[^A-Z0-9]+", "_", str(k).upper()).strip("_")
        lines.append(f"{prefix}_{key_name}={v}")

    content = "\n".join(lines) + "\n"
    env_path = dest_dir / ".env"
    env_path.write_text(content, encoding="utf-8")


def ensure_volume_directories(config: Dict[str, Any]) -> None:
    """Create directories for each host path volume if not present (best-effort)."""
    try:
        volume_mappings = parse_volumes(config)
    except Exception:
        return
    for src, _dst in volume_mappings:
        normalized_src = normalize_host_path(src)
        # Ignore when this seems like a named volume (no path separator)
        if os.path.isabs(normalized_src) or os.sep in normalized_src:
            try:
                os.makedirs(normalized_src, exist_ok=True)
            except Exception:
                # Best-effort; if it fails, let compose handle it
                pass


def rewrite_compose_with_env(dest_dir: Path, honeypot_id: str, honeypot_name: str, config: Dict[str, Any]) -> None:
    """
    Modify docker-compose.yml so that:
      - ports: uses "${PREFIX_PORTn_SRC}:${PREFIX_PORTn_DST}"
      - volumes: uses "${PREFIX_VOLn_SRC}:${PREFIX_VOLn_DST}"
      - environment: if `env` exists in honeypots YAML, set KEY: "${PREFIX_KEY}"
      - image: if `image` exists in honeypots YAML, set service image accordingly
    """
    compose_path = dest_dir / "docker-compose.yml"
    if not compose_path.exists():
        return

    with compose_path.open("r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f) or {}

    if not isinstance(compose_data, dict):
        return

    services = compose_data.get("services")
    if not isinstance(services, dict) or not services:
        return

    prefix = to_var_prefix(honeypot_name)

    # Optional: pick subset of services based on config ('service' or 'services' keys)
    selected_service_names: List[str] = []
    if isinstance(config.get("service"), str) and config.get("service"):
        selected_service_names = [str(config.get("service"))]
    elif isinstance(config.get("services"), list):
        selected_service_names = [str(s) for s in config.get("services") if isinstance(s, (str, int))]

    if selected_service_names:
        filtered: Dict[str, Any] = {}
        for name in selected_service_names:
            if name in services and isinstance(services[name], dict):
                filtered[name] = services[name]
        if not filtered:
            # If names do not match, do nothing to avoid breaking compose
            pass
        else:
            compose_data["services"] = services = filtered

    # Prepare string lists for ports/volumes
    ports_pairs: List[Tuple[str, str]] = []
    volumes_pairs: List[Tuple[str, str]] = []

    try:
        ports_pairs = parse_ports(config)
    except Exception:
        ports_pairs = []

    try:
        volumes_pairs = parse_volumes(config)
    except Exception:
        volumes_pairs = []

    ports_expr: List[str] = [f"${{{prefix}_PORT{i}_SRC}}:${{{prefix}_PORT{i}_DST}}" for i in range(1, len(ports_pairs) + 1)]
    volumes_expr: List[str] = [f"${{{prefix}_VOL{i}_SRC}}:${{{prefix}_VOL{i}_DST}}" for i in range(1, len(volumes_pairs) + 1)]

    env_map = parse_env(config) if isinstance(config.get("env"), dict) else {}
    env_expr_map: Dict[str, str] = {}
    for k in env_map.keys():
        key_name = re.sub(r"[^A-Z0-9]+", "_", str(k).upper()).strip("_")
        env_expr_map[str(k)] = f"${{{prefix}_{key_name}}}"

    cfg_image = config.get("image")

    # Apply to all services
    for svc_name, svc in services.items():
        if not isinstance(svc, dict):
            continue

        if ports_expr:
            svc["ports"] = ports_expr.copy()

        if volumes_expr:
            svc["volumes"] = volumes_expr.copy()

        if env_expr_map:
            # Merge dengan environment yang sudah ada, namun overwrite key yang sama agar konsisten dengan honeypots YAML
            current_env = svc.get("environment")
            if isinstance(current_env, dict):
                merged = dict(current_env)
                for k, v in env_expr_map.items():
                    merged[k] = v
                svc["environment"] = merged
            elif isinstance(current_env, list):
                # Ubah list ke dict jika memungkinkan (format KEY=val)
                temp: Dict[str, str] = {}
                for item in current_env:
                    if isinstance(item, str) and "=" in item:
                        k, v = item.split("=", 1)
                        temp[k] = v
                for k, v in env_expr_map.items():
                    temp[k] = v
                svc["environment"] = temp
            else:
                svc["environment"] = env_expr_map.copy()

        if isinstance(cfg_image, str) and cfg_image.strip():
            svc["image"] = cfg_image.strip()

    # Simpan kembali compose
    with compose_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            compose_data,
            f,
            default_flow_style=False,
            sort_keys=False,
        )
