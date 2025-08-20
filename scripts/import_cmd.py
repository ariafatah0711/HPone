"""
Import Helpers untuk HPone

Fungsi-fungsi untuk mengimport template tools.
"""

from pathlib import Path
from typing import Dict, Any

# Import constants dan functions dari helpers
from core.constants import OUTPUT_DOCKER_DIR
from core.yaml import load_tool_yaml_by_filename
from .file_ops import ensure_destination_dir, find_template_dir, copy_template_to_destination
from core.config import ensure_volume_directories, generate_env_file, rewrite_compose_with_env


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
