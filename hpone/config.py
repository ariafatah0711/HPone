#!/usr/bin/env python3
"""
HPone Configuration File

File ini berisi konfigurasi path yang bisa diubah oleh user.
"""

from pathlib import Path

# Lokasi direktori root project (folder tempat file ini berada)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Konfigurasi behavior
ALWAYS_IMPORT = True          # True: hide import/remove commands, auto-import on up

# Lokasi direktori honeypots (berisi file YAML honeypot)
HONEYPOT_MANIFEST_DIR = PROJECT_ROOT / "honeypots"
# Lokasi direktori template Docker
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
# Lokasi direktori output Docker (tempat hasil import)
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"
# Lokasi direktori data untuk mount (hanya dihapus ketika clean --data)
DATA_DIR = PROJECT_ROOT / "data"

# Konfigurasi untuk list command
LIST_BASIC_MAX_WIDTH = 80      # Max width untuk list biasa
LIST_DETAILED_MAX_WIDTH = 30   # Max width untuk list -a (detailed)

# Konfigurasi logging
USE_EPHEMERAL_LOGGING = True  # True: use ephemeral logging for up/down commands, False: use simple output
