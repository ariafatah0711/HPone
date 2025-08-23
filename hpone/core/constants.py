"""
Constants untuk HPone Core

File ini berisi constants yang dibutuhkan oleh semua core modules.
Sekarang menggunakan konfigurasi dari config.py yang bisa diubah user.
"""

from pathlib import Path
import sys

# Tentukan PROJECT_ROOT dengan cara yang lebih robust
# Cari file app.py di parent directories untuk menentukan root project
def find_project_root() -> Path:
    """Find the project root by looking for app.py file."""
    current_path = Path(__file__).resolve().parent

    # Naik ke parent directories sampai ketemu app.py
    for parent in [current_path] + list(current_path.parents):
        if (parent / "app.py").exists() and (parent / "honeypots").exists():
            return parent

    # Fallback: assume structure hpone/core/constants.py
    return Path(__file__).resolve().parent.parent.parent

PROJECT_ROOT = find_project_root()

# Import konfigurasi dari file config.py di hpone directory
try:
    # Add parent directory to path to import config
    config_dir = PROJECT_ROOT / "hpone"
    if str(config_dir) not in sys.path:
        sys.path.insert(0, str(config_dir))

    from config import (
        HONEYPOT_MANIFEST_DIR as CONFIG_HONEYPOT_MANIFEST_DIR,
        TEMPLATE_DOCKER_DIR as CONFIG_TEMPLATE_DOCKER_DIR,
        OUTPUT_DOCKER_DIR as CONFIG_OUTPUT_DOCKER_DIR,
        DATA_DIR as CONFIG_DATA_DIR,
    )
    HONEYPOT_MANIFEST_DIR = CONFIG_HONEYPOT_MANIFEST_DIR
    TEMPLATE_DOCKER_DIR = CONFIG_TEMPLATE_DOCKER_DIR
    OUTPUT_DOCKER_DIR = CONFIG_OUTPUT_DOCKER_DIR
    DATA_DIR = CONFIG_DATA_DIR
except ImportError:
    # Fallback ke default values jika config.py tidak ditemukan
    HONEYPOT_MANIFEST_DIR = PROJECT_ROOT / "honeypots"
    TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
    OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"
    DATA_DIR = PROJECT_ROOT / "data"
