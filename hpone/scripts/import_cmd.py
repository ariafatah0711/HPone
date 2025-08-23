"""
Import helpers for HPone.

Functions to import honeypot templates.
"""

from pathlib import Path
from typing import Dict, Any

# Import constants dan functions dari helpers
from core.constants import OUTPUT_DOCKER_DIR
from core.yaml import load_honeypot_yaml_by_filename
from .file_ops import ensure_destination_dir, find_template_dir, copy_template_to_destination
from core.config import ensure_volume_directories, generate_env_file, rewrite_compose_with_env
from core.utils import PREFIX_WARN


def import_honeypot(honeypot_id: str, force: bool = False) -> Path:
    resolved_name, cfg = load_honeypot_yaml_by_filename(honeypot_id)
    dest_dir = OUTPUT_DOCKER_DIR / honeypot_id

    # Check if template exists BEFORE creating destination directory
    template_dir = find_template_dir(honeypot_id)

    # Only create destination directory if template is found
    ensure_destination_dir(dest_dir, force=force)
    copy_template_to_destination(template_dir, dest_dir)
    # Ensure host directories for volumes exist
    ensure_volume_directories(cfg)
    generate_env_file(dest_dir, resolved_name, cfg)
    try:
        rewrite_compose_with_env(dest_dir, honeypot_id, resolved_name, cfg)
    except Exception as exc:
        # Non-fatal: continue even if rewrite fails
        print(f"{PREFIX_WARN} Failed to adjust docker-compose.yml for env: {exc}")

    return dest_dir
