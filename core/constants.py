"""
Constants untuk HPone Core

File ini berisi constants yang dibutuhkan oleh semua core modules.
Sekarang menggunakan konfigurasi dari config.py yang bisa diubah user.
"""

from pathlib import Path

# Import konfigurasi dari file config.py di root project
try:
    from config import (
        PROJECT_ROOT,
        TOOLS_DIR,
        TEMPLATE_DOCKER_DIR,
        OUTPUT_DOCKER_DIR,
    )
except ImportError:
    # Fallback ke default values jika config.py tidak ditemukan
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    TOOLS_DIR = PROJECT_ROOT / "tools"
    TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
    OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"