"""
Constants untuk HPone Core

File ini berisi constants yang dibutuhkan oleh semua core modules.
"""

from pathlib import Path

# Lokasi direktori root project (folder tempat file ini berada)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"
