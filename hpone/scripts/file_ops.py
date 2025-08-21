"""
File helpers for HPone.

Functions to manage files, directories, and templates.
"""

import shutil
from pathlib import Path
from typing import Dict, Any

# Import constants dari helpers
from core.constants import TEMPLATE_DOCKER_DIR, OUTPUT_DOCKER_DIR
from core.utils import PREFIX_OK, PREFIX_WARN, PREFIX_ERROR

def ensure_destination_dir(dest: Path, force: bool = False) -> None:
    if dest.exists():
        if force:
            shutil.rmtree(dest)
        else:
            raise FileExistsError(f"Destination directory already exists: {dest}. Use --force to overwrite.")
    dest.mkdir(parents=True, exist_ok=True)


def find_template_dir(tool_id: str) -> Path:
    """
    Locate template directory:
      1) template/docker/<tool_id>/
      2) If not present, and template/docker/ contains 'Dockerfile' and 'docker-compose.yml' directly, use that.
    """
    tool_dir = TEMPLATE_DOCKER_DIR / tool_id
    if tool_dir.exists() and tool_dir.is_dir():
        return tool_dir

    dockerfile = TEMPLATE_DOCKER_DIR / "Dockerfile"
    compose = TEMPLATE_DOCKER_DIR / "docker-compose.yml"
    if dockerfile.exists() and compose.exists():
        return TEMPLATE_DOCKER_DIR

    # Helpful info
    available = sorted([p.name for p in TEMPLATE_DOCKER_DIR.glob("*/") if p.is_dir()])
    raise FileNotFoundError(
        f"Template not found. Expected '{TEMPLATE_DOCKER_DIR}/<tool>/' or common files 'Dockerfile' and 'docker-compose.yml'. "
        f"Requested tool: '{tool_id}'. Available templates: {', '.join(available) if available else '-'}"
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

    # If tool-specific template (contains dist/, etc.), copy the tree
    for item in template_dir.iterdir():
        src = item
        dst = dest_dir / item.name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def remove_tool(tool_id: str) -> None:
    dest_dir = OUTPUT_DOCKER_DIR / tool_id
    if not dest_dir.exists():
        print(f"{PREFIX_WARN} Folder not found: {dest_dir}")
        return
    shutil.rmtree(dest_dir)
    print(f"{PREFIX_OK}: Removed tool {tool_id}")
