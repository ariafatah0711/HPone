"""
File helpers for HPone.

Functions to manage files, directories, and templates.
"""

import shutil
from pathlib import Path
from typing import Dict, Any

# Import constants dari helpers
from core.constants import TEMPLATE_DOCKER_DIR, OUTPUT_DOCKER_DIR, DATA_DIR
from core.utils import PREFIX_OK, PREFIX_WARN, PREFIX_ERROR

def ensure_destination_dir(dest: Path, force: bool = False) -> None:
    if dest.exists():
        if force:
            shutil.rmtree(dest)
        else:
            raise FileExistsError(f"Destination directory already exists: {dest}. Use --force to overwrite.")
    dest.mkdir(parents=True, exist_ok=True)


def find_template_dir(honeypot_id: str) -> Path:
    """
    Locate template directory with support for custom template_dir from YAML:
      1) If honeypot YAML has 'template_dir' field, use that custom path
      2) template/docker/<honeypot_id>/
      3) If not present, and template/docker/ contains 'Dockerfile' and 'docker-compose.yml' directly, use that.
    """
    # Check for custom template directory in YAML config
    try:
        from core.yaml import get_custom_template_dir
        custom_template = get_custom_template_dir(honeypot_id)
        if custom_template and custom_template.exists() and custom_template.is_dir():
            # Verify custom template has required files
            dockerfile = custom_template / "Dockerfile"
            compose = custom_template / "docker-compose.yml"
            if dockerfile.exists() and compose.exists():
                return custom_template
            else:
                print(f"{PREFIX_WARN} Custom template directory '{custom_template}' missing required files (Dockerfile, docker-compose.yml)")
    except Exception as e:
        print(f"{PREFIX_WARN} Failed to check custom template directory: {e}")

    # Fallback to standard template discovery
    honeypot_dir = TEMPLATE_DOCKER_DIR / honeypot_id
    if honeypot_dir.exists() and honeypot_dir.is_dir():
        return honeypot_dir

    dockerfile = TEMPLATE_DOCKER_DIR / "Dockerfile"
    compose = TEMPLATE_DOCKER_DIR / "docker-compose.yml"
    if dockerfile.exists() and compose.exists():
        return TEMPLATE_DOCKER_DIR

    # Helpful info
    available = sorted([p.name for p in TEMPLATE_DOCKER_DIR.glob("*/") if p.is_dir()])
    raise FileNotFoundError(
        f"Template not found. Expected custom 'template_dir' in YAML, '{TEMPLATE_DOCKER_DIR}/<honeypot>/' or common files 'Dockerfile' and 'docker-compose.yml'. "
        f"Requested honeypot: '{honeypot_id}'. Available templates: {', '.join(available) if available else '-'}"
    )


def copy_template_to_destination(template_dir: Path, dest_dir: Path) -> None:
    """Copy template contents to the destination directory."""
    # If using TEMPLATE_DOCKER_DIR as a generic template, copy only Dockerfile and docker-compose.yml
    if template_dir == TEMPLATE_DOCKER_DIR:
        for fname in ("Dockerfile", "docker-compose.yml"):
            src = template_dir / fname
            if src.exists():
                shutil.copy2(src, dest_dir / fname)
        return

    # If honeypot-specific template (contains dist/, etc.), copy the tree
    for item in template_dir.iterdir():
        src = item
        dst = dest_dir / item.name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def remove_honeypot(honeypot_id: str) -> None:
    dest_dir = OUTPUT_DOCKER_DIR / honeypot_id
    if not dest_dir.exists():
        print(f"{PREFIX_WARN} Folder not found: {dest_dir}")
        return
    shutil.rmtree(dest_dir)
    print(f"{PREFIX_OK}: Removed honeypot {honeypot_id}")


def remove_honeypot_data(honeypot_id: str) -> bool:
    """
    Remove mounted data directory for a honeypot inside DATA_DIR.
    Only deletes if path is strictly within DATA_DIR and equals DATA_DIR/honeypot_id.

    Returns True if data was removed, False if nothing removed.
    """
    try:
        base = DATA_DIR.resolve()
    except Exception:
        base = DATA_DIR
    target = (DATA_DIR / honeypot_id)
    try:
        target_resolved = target.resolve()
    except Exception:
        target_resolved = target

    # Safety checks: target exists, is a directory, and under base, and exactly base/honeypot_id
    if not target.exists() or not target.is_dir():
        print(f"{PREFIX_WARN} Data folder not found: {target}")
        return False
    try:
        # Ensure target_resolved is under base
        target_resolved.relative_to(base)
    except Exception:
        print(f"{PREFIX_ERROR} Refuse to remove data outside DATA_DIR: {target_resolved}")
        return False
    # Ensure the immediate path matches DATA_DIR/honeypot_id (not deeper arbitrary)
    if target_resolved != (base / honeypot_id):
        print(f"{PREFIX_ERROR} Refuse to remove unexpected path: {target_resolved}")
        return False

    shutil.rmtree(target_resolved)
    print(f"{PREFIX_OK}: Removed data for {honeypot_id}")
    return True
