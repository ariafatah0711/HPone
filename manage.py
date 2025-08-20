#!/usr/bin/env python3
"""
HPone Docker template manager.

Perintah:
  - list                   : Tampilkan daftar tools berdasarkan YAML di `tools/` dan status imported.
  - import <tool> [--force] : Import template ke folder `docker/<tool>/` dan generate file `.env` dari `tools/<tool>.yml`.
  - import --all [--force] : Import semua tool yang enabled.
  - remove <tool>          : Hapus folder `docker/<tool>/`.
  - remove --all           : Hapus semua tool yang sudah diimport.
  - enable <tool>          : Set `enabled: true` pada `tools/<tool>.yml`.
  - disable <tool>         : Set `enabled: false` pada `tools/<tool>.yml`.
  - up [<tool> | --all]    : Jalankan `docker compose up -d` untuk satu tool atau semua tool yang enabled.
  - down [<tool> | --all]  : Jalankan `docker compose down` untuk satu tool atau semua tool yang diimport.

Contoh:
  python manage.py import cowrie
  python manage.py import --all
  python manage.py list
  python manage.py list -a
  python manage.py remove cowrie
  python manage.py remove --all
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    print("[ERROR] Modul PyYAML belum terpasang. Tambahkan ke environment Anda atau jalankan: pip install -r requirements.txt", file=sys.stderr)
    raise


# Lokasi direktori root project (folder tempat file ini berada)
PROJECT_ROOT = Path(__file__).resolve().parent
TOOLS_DIR = PROJECT_ROOT / "tools"
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"


def to_var_prefix(tool_name: str) -> str:
    """Konversi nama tool menjadi prefix ENV uppercase yang aman: cowrie -> COWRIE."""
    upper = tool_name.strip().upper()
    return re.sub(r"[^A-Z0-9]+", "_", upper).strip("_")


def load_tool_yaml_by_filename(tool_id: str) -> Tuple[str, Dict[str, Any]]:
    """
    Baca YAML `tools/<tool_id>.yml`. Jika tidak ada, coba cari file YAML yang memiliki `name: <tool_id>` (case-insensitive).
    Return (resolved_tool_name, config_dict).
    """
    explicit_path = TOOLS_DIR / f"{tool_id}.yml"
    if explicit_path.exists():
        with explicit_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        resolved_name = str(data.get("name") or tool_id)
        return resolved_name, data

    # Fallback: cari berdasarkan field `name`
    for path_str in glob.glob(str(TOOLS_DIR / "*.yml")):
        p = Path(path_str)
        try:
            with p.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if str(data.get("name", "")).lower() == tool_id.lower():
                return str(data.get("name")), data
        except Exception:
            continue

    raise FileNotFoundError(f"Config YAML untuk tool '{tool_id}' tidak ditemukan di '{TOOLS_DIR}'.")


def find_tool_yaml_path(tool_id: str) -> Path:
    """Balikkan path YAML untuk tool_id berdasarkan nama file atau field `name` di dalam YAML."""
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
    raise FileNotFoundError(f"File YAML untuk tool '{tool_id}' tidak ditemukan di '{TOOLS_DIR}'.")


def set_tool_enabled(tool_id: str, enabled: bool) -> None:
    """Ubah field `enabled` pada `tools/<tool>.yml`. Mencari berdasarkan nama file atau field `name`."""
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


def is_tool_running(tool_id: str) -> bool:
    """Check if tool is running by checking Docker container status."""
    try:
        dir_id = resolve_tool_dir_id(tool_id)
        dest_dir = OUTPUT_DOCKER_DIR / dir_id
        if not dest_dir.exists():
            return False

        # Check if any containers for this tool are running
        cmd = ["docker", "compose", "ps", "--format", "json"]
        try:
            result = subprocess.run(cmd, cwd=str(dest_dir), capture_output=True, text=True, check=True)
            # If output is not empty and contains running containers
            if result.stdout.strip():
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to docker-compose v1
            try:
                cmd_legacy = ["docker-compose", "ps", "--format", "json"]
                result = subprocess.run(cmd_legacy, cwd=str(dest_dir), capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        return False
    except Exception:
        return False

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
    """Dapatkan semua tool yang enabled (tidak perlu sudah diimport)."""
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
        yaml_path = find_tool_yaml_path(tool_id)
        candidate = Path(yaml_path).stem
        if (OUTPUT_DOCKER_DIR / candidate).exists():
            return candidate
    except FileNotFoundError:
        pass
    return tool_id


def run_compose_action(tool_dir: Path, action: str) -> None:
    if not (tool_dir / "docker-compose.yml").exists():
        raise FileNotFoundError(f"docker-compose.yml tidak ditemukan di {tool_dir}")

    cmd_dc = ["docker", "compose", action]
    if action == "up":
        cmd_dc.append("-d")

    try:
        subprocess.run(cmd_dc, cwd=str(tool_dir), check=True)
        return
    except FileNotFoundError:
        # Fallback ke docker-compose v1
        cmd_legacy = ["docker-compose", action]
        if action == "up":
            cmd_legacy.append("-d")
        subprocess.run(cmd_legacy, cwd=str(tool_dir), check=True)


def up_tool(tool_id: str, force: bool = False) -> None:
    dir_id = resolve_tool_dir_id(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / dir_id
    if not dest_dir.exists():
        raise FileNotFoundError(f"Folder docker untuk tool '{tool_id}' tidak ditemukan: {dest_dir}. Jalankan 'import' terlebih dahulu.")

    # Check if tool is enabled (unless force is used)
    if not force and not is_tool_enabled(tool_id):
        raise ValueError(f"Tool '{tool_id}' tidak enabled. Jalankan 'enable {tool_id}' terlebih dahulu atau gunakan --force.")

    print(f"[UP] {dir_id} ...", flush=True)
    run_compose_action(dest_dir, "up")
    print(f"[UP] {dir_id} OK")


def down_tool(tool_id: str) -> None:
    dir_id = resolve_tool_dir_id(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / dir_id
    if not dest_dir.exists():
        print(f"[DOWN] Skip {dir_id}: folder tidak ada.")
        return
    print(f"[DOWN] {dir_id} ...", flush=True)
    run_compose_action(dest_dir, "down")
    print(f"[DOWN] {dir_id} OK")


def ensure_destination_dir(dest: Path, force: bool = False) -> None:
    if dest.exists():
        if force:
            shutil.rmtree(dest)
        else:
            raise FileExistsError(f"Folder tujuan sudah ada: {dest}. Gunakan --force untuk overwrite.")
    dest.mkdir(parents=True, exist_ok=True)


def find_template_dir(tool_id: str) -> Path:
    """
    Cari template:
      1) template/docker/<tool_id>/
      2) Jika tidak ada, dan template/docker/ berisi langsung file 'Dockerfile' dan 'docker-compose.yml', gunakan itu.
    """
    tool_dir = TEMPLATE_DOCKER_DIR / tool_id
    if tool_dir.exists() and tool_dir.is_dir():
        return tool_dir

    dockerfile = TEMPLATE_DOCKER_DIR / "Dockerfile"
    compose = TEMPLATE_DOCKER_DIR / "docker-compose.yml"
    if dockerfile.exists() and compose.exists():
        return TEMPLATE_DOCKER_DIR

    # Info bantuan
    available = sorted([p.name for p in TEMPLATE_DOCKER_DIR.glob("*/") if p.is_dir()])
    raise FileNotFoundError(
        "Template tidak ditemukan. Harus ada 'template/docker/<tool>/' atau file umum 'template/docker/Dockerfile' dan 'docker-compose.yml'. "
        f"Tool dicari: '{tool_id}'. Template tersedia: {', '.join(available) if available else '-'}"
    )


def copy_template_to_destination(template_dir: Path, dest_dir: Path) -> None:
    """Salin seluruh isi template ke folder tujuan."""
    # Jika template_dir == TEMPLATE_DOCKER_DIR (mode umum), salin hanya Dockerfile dan docker-compose.yml
    if template_dir == TEMPLATE_DOCKER_DIR:
        for fname in ("Dockerfile", "docker-compose.yml"):
            src = template_dir / fname
            if src.exists():
                shutil.copy2(src, dest_dir / fname)
        return

    # Jika template spesifik tool (berisi dist/, dsb), copy tree
    for item in template_dir.iterdir():
        src = item
        dst = dest_dir / item.name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def parse_ports(config: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Kembalikan list tuple (host_src, container_dst). Mendukung format dict atau string 'host:container'."""
    result: List[Tuple[str, str]] = []
    ports = config.get("ports") or []
    for entry in ports:
        if isinstance(entry, dict):
            # Mendukung kunci 'host'/'container' atau 'src'/'dst'
            host = entry.get("host") or entry.get("src") or entry.get("source")
            container = entry.get("container") or entry.get("dst") or entry.get("destination")
            if host is not None and container is not None:
                result.append((str(host), str(container)))
                continue
        if isinstance(entry, str):
            # Format "2222:22" → ambil bagian kiri dan kanan pertama
            if ":" in entry:
                left, right = entry.split(":", 1)
                result.append((left.strip(), right.strip()))
                continue
        raise ValueError(f"Format port tidak dikenali: {entry!r}")
    return result


def parse_volumes(config: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Kembalikan list tuple (src, dst). Mendukung string 'src:dst' atau dict {'src'/'dst'} atau {'host'/'container'}."""
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
                # Ambil dua bagian pertama sebagai src dan dst (abaikan mode tambahan seperti :ro jika ada)
                left, right = entry.split(":", 1)
                # Jika masih ada ":" di kanan (mis. dst:ro), ambil hanya path tujuan sebelum mode
                if ":" in right:
                    dst_path, _mode = right.split(":", 1)
                    result.append((left.strip(), dst_path.strip()))
                else:
                    result.append((left.strip(), right.strip()))
                continue
        raise ValueError(f"Format volume tidak dikenali: {entry!r}")
    return result


def parse_env(config: Dict[str, Any]) -> Dict[str, str]:
    env_mapping: Dict[str, str] = {}
    env = config.get("env") or {}
    if isinstance(env, dict):
        for k, v in env.items():
            env_mapping[str(k)] = "" if v is None else str(v)
    else:
        raise ValueError("Field 'env' harus berupa mapping/dict jika ada.")
    return env_mapping


def normalize_host_path(path_str: str) -> str:
    """Normalisasi path host untuk volumes:
    - Ekspansi env var (mis. $HOME) dan ~
    - Jika relatif, jadikan absolut relatif ke root proyek
    """
    if not isinstance(path_str, str) or not path_str:
        return path_str
    # Expand env vars dan ~
    expanded = os.path.expandvars(os.path.expanduser(path_str))
    # Jika masih relatif, buat absolut relatif ke root project
    if not os.path.isabs(expanded):
        try:
            absolute = str((PROJECT_ROOT / expanded).resolve())
        except Exception:
            absolute = str(PROJECT_ROOT / expanded)
        return absolute
    return expanded

def generate_env_file(dest_dir: Path, tool_name: str, config: Dict[str, Any]) -> None:
    """Buat file `.env` di folder tujuan berdasarkan config YAML."""
    prefix = to_var_prefix(tool_name)

    lines: List[str] = []
    lines.append(f"# Auto-generated by manage.py for {tool_name}")

    # Ports
    try:
        port_mappings = parse_ports(config)
    except Exception as exc:
        raise ValueError(f"Gagal parsing 'ports': {exc}")

    for idx, (host_src, container_dst) in enumerate(port_mappings, start=1):
        lines.append(f"{prefix}_PORT{idx}_SRC={host_src}")
        lines.append(f"{prefix}_PORT{idx}_DST={container_dst}")

    # Volumes
    try:
        volume_mappings = parse_volumes(config)
    except Exception as exc:
        raise ValueError(f"Gagal parsing 'volumes': {exc}")

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
    """Buat direktori untuk setiap host path volume jika belum ada (best-effort)."""
    try:
        volume_mappings = parse_volumes(config)
    except Exception:
        return
    for src, _dst in volume_mappings:
        normalized_src = normalize_host_path(src)
        # Abaikan jika ini kemungkinan named volume (tanpa path separator)
        if os.path.isabs(normalized_src) or os.sep in normalized_src:
            try:
                os.makedirs(normalized_src, exist_ok=True)
            except Exception:
                # Best-effort, jika gagal biarkan compose yang mengelola
                pass


def rewrite_compose_with_env(dest_dir: Path, tool_id: str, tool_name: str, config: Dict[str, Any]) -> None:
    """
    Modifikasi docker-compose.yml agar:
      - ports: menggunakan "${PREFIX_PORTn_SRC}:${PREFIX_PORTn_DST}"
      - volumes: menggunakan "${PREFIX_VOLn_SRC}:${PREFIX_VOLn_DST}"
      - environment: jika ada `env` di YAML tools, set KEY: "${PREFIX_KEY}"
      - image: jika ada `image` di YAML tools, set image service -> value tsb
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

    prefix = to_var_prefix(tool_name)

    # Optional: pilih subset service berdasarkan config (kunci 'service' atau 'services')
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
            # Jika nama tidak cocok, jangan lakukan apa-apa agar tidak memecah compose
            pass
        else:
            compose_data["services"] = services = filtered

    # Siapkan daftar string untuk ports/volumes
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

    # Terapkan ke semua services yang ada
    for svc_name, svc in services.items():
        if not isinstance(svc, dict):
            continue

        if ports_expr:
            svc["ports"] = ports_expr.copy()

        if volumes_expr:
            svc["volumes"] = volumes_expr.copy()

        if env_expr_map:
            # Merge dengan environment yang sudah ada, namun overwrite key yang sama agar konsisten dengan tools YAML
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

def import_tool(tool_id: str, force: bool = False) -> Path:
    resolved_name, cfg = load_tool_yaml_by_filename(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / tool_id

    ensure_destination_dir(dest_dir, force=force)
    template_dir = find_template_dir(tool_id)
    copy_template_to_destination(template_dir, dest_dir)
    # Pastikan direktori host untuk volume tersedia
    ensure_volume_directories(cfg)
    generate_env_file(dest_dir, resolved_name, cfg)
    try:
        rewrite_compose_with_env(dest_dir, tool_id, resolved_name, cfg)
    except Exception as exc:
        # Tidak fatal: tetap lanjut meskipun rewrite gagal
        print(f"[WARN] Gagal menyesuaikan docker-compose.yml untuk env: {exc}")

    return dest_dir


def _format_table(headers: List[str], rows: List[List[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if len(str(cell)) > widths[i]:
                widths[i] = len(str(cell))
    sep = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    out_lines: List[str] = []
    out_lines.append(sep)
    header_line = "|" + "|".join([" " + headers[i].ljust(widths[i]) + " " for i in range(len(headers))]) + "|"
    out_lines.append(header_line)
    out_lines.append(sep)
    for row in rows:
        line = "|" + "|".join([" " + str(row[i]).ljust(widths[i]) + " " for i in range(len(headers))]) + "|"
        out_lines.append(line)
    out_lines.append(sep)
    return "\n".join(out_lines)


def list_tools(detailed: bool = False) -> None:
    yaml_files = sorted(glob.glob(str(TOOLS_DIR / "*.yml")))
    if not yaml_files:
        print("Tidak ada file YAML di folder 'tools/'.")
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
        running_flag = is_tool_running(p.stem)

        enabled_str = "True" if enabled_flag else "False"
        status_str = "UP" if running_flag else "DOWN"

        rows_basic.append([name, enabled_str, status_str, description])

        if detailed:
            # Ports
            ports_info = ""
            try:
                ports = parse_ports(data)
                if ports:
                    ports_info = ", ".join([f"{host}:{container}" for host, container in ports])
            except Exception:
                ports_info = "(error parsing)"
            # Volumes
            volumes_info = ""
            try:
                vols = parse_volumes(data)
                if vols:
                    volumes_info = ", ".join([f"{src}:{dst}" for src, dst in vols])
            except Exception:
                volumes_info = "(error parsing)"

            rows_detail.append([name, description, ports_info, volumes_info])

    if detailed:
        table = _format_table(["TOOL", "DESCRIPTION", "PORTS", "VOLUMES"], rows_detail)
    else:
        table = _format_table(["TOOL", "ENABLED", "STATUS", "DESCRIPTION"], rows_basic)

    print(table)

def remove_tool(tool_id: str) -> None:
    dest_dir = OUTPUT_DOCKER_DIR / tool_id
    if not dest_dir.exists():
        print(f"Folder tidak ditemukan: {dest_dir}")
        return
    shutil.rmtree(dest_dir)
    print(f"Removed: {dest_dir}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HPone Docker template manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_import = sub.add_parser("import", help="Import template dan generate .env untuk tool")
    p_import.add_argument("tool", nargs="?", help="Nama tool (sesuai nama file YAML di folder tools/)")
    p_import.add_argument("--all", action="store_true", help="Import semua tool yang enabled")
    p_import.add_argument("--force", action="store_true", help="Overwrite folder docker/<tool> jika sudah ada")

    p_list = sub.add_parser("list", help="List tools berdasarkan YAML di folder tools/")
    p_list.add_argument("-a", action="store_true", help="Tampilkan detail lengkap (deskripsi dan ports)")

    p_remove = sub.add_parser("remove", help="Hapus folder docker/<tool>")
    p_remove.add_argument("tool", nargs="?", help="Nama tool yang akan dihapus")
    p_remove.add_argument("--all", action="store_true", help="Hapus semua tool yang sudah diimport")

    p_enable = sub.add_parser("enable", help="Enable tool pada tools/<tool>.yml (set enabled: true)")
    p_enable.add_argument("tool", help="Nama tool yang akan di-enable")

    p_disable = sub.add_parser("disable", help="Disable tool pada tools/<tool>.yml (set enabled: false)")
    p_disable.add_argument("tool", help="Nama tool yang akan di-disable")

    p_up = sub.add_parser("up", help="docker compose up -d untuk satu tool atau semua tool yang enabled")
    group_up = p_up.add_mutually_exclusive_group(required=True)
    group_up.add_argument("tool", nargs="?", help="Nama tool. Jika tidak diberikan, gunakan --all")
    group_up.add_argument("--all", action="store_true", help="Jalankan untuk semua tool yang enabled dan sudah diimport")
    p_up.add_argument("--force", action="store_true", help="Force up tool meskipun tidak enabled (hanya untuk single tool)")

    p_down = sub.add_parser("down", help="docker compose down untuk satu tool atau semua tool yang diimport")
    group_down = p_down.add_mutually_exclusive_group(required=True)
    group_down.add_argument("tool", nargs="?", help="Nama tool. Jika tidak diberikan, gunakan --all")
    group_down.add_argument("--all", action="store_true", help="Jalankan untuk semua tool yang diimport")

    return parser

def main(argv: List[str]) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.command == "import":
        try:
            if getattr(args, "all", False):
                # Import semua tool yang enabled
                tool_ids = list_all_enabled_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool yang enabled.")
                    return 0
                print(f"Importing {len(tool_ids)} enabled tools...")
                for t in tool_ids:
                    try:
                        dest = import_tool(t, force=bool(args.force))
                        print(f"OK: Template '{t}' diimport ke: {dest}")
                    except Exception as exc:
                        print(f"[ERROR] Gagal import '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                dest = import_tool(args.tool, force=bool(args.force))
                print(f"OK: Template '{args.tool}' diimport ke: {dest}")
                print(f"OK: File .env dibuat di: {dest / '.env'}")
        except Exception as exc:
            print(f"[ERROR] Gagal import: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "list":
        try:
            list_tools(detailed=bool(args.a))
        except Exception as exc:
            print(f"[ERROR] Gagal list tools: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "remove":
        try:
            if getattr(args, "all", False):
                # Remove semua tool yang sudah diimport
                tool_ids = list_imported_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool yang diimport.")
                    return 0
                print(f"Removing {len(tool_ids)} imported tools...")
                for t in tool_ids:
                    try:
                        remove_tool(t)
                    except Exception as exc:
                        print(f"[ERROR] Gagal remove '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                remove_tool(args.tool)
        except Exception as exc:
            print(f"[ERROR] Gagal remove: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "enable":
        try:
            set_tool_enabled(args.tool, True)
        except Exception as exc:
            print(f"[ERROR] Gagal enable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"OK: Tool '{args.tool}' enabled.")
        return 0

    if args.command == "disable":
        try:
            set_tool_enabled(args.tool, False)
        except Exception as exc:
            print(f"[ERROR] Gagal disable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"OK: Tool '{args.tool}' disabled.")
        return 0

    if args.command == "up":
        try:
            if getattr(args, "all", False):
                # For --all, ignore force flag and only up enabled tools
                tool_ids = list_enabled_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool enabled yang sudah diimport.")
                for t in tool_ids:
                    up_tool(t, force=False)
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                up_tool(args.tool, force=bool(args.force))
        except Exception as exc:
            print(f"[ERROR] Gagal up: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "down":
        try:
            if getattr(args, "all", False):
                tool_ids = list_imported_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool yang diimport.")
                for t in tool_ids:
                    down_tool(t)
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                down_tool(args.tool)
        except Exception as exc:
            print(f"[ERROR] Gagal down: {exc}", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))