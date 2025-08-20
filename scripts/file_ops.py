"""
File Helpers untuk HPone

Fungsi-fungsi untuk mengelola file, direktori, dan template.
"""

import shutil
from pathlib import Path
from typing import Dict, Any

# Import constants dari helpers
from core.constants import TEMPLATE_DOCKER_DIR, OUTPUT_DOCKER_DIR

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


def remove_tool(tool_id: str) -> None:
    dest_dir = OUTPUT_DOCKER_DIR / tool_id
    if not dest_dir.exists():
        print(f"Folder tidak ditemukan: {dest_dir}")
        return
    shutil.rmtree(dest_dir)
    print(f"Removed: {dest_dir}")
