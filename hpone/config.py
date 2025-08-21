#!/usr/bin/env python3
"""
HPone Configuration File

File ini berisi konfigurasi path yang bisa diubah oleh user.
"""

from pathlib import Path

# Lokasi direktori root project (folder tempat file ini berada)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Lokasi direktori tools (berisi file YAML honeypot)
TOOLS_DIR = PROJECT_ROOT / "tools"

# Lokasi direktori template Docker
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"

# Lokasi direktori output Docker (tempat hasil import)
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"

# Konfigurasi untuk list command
LIST_BASIC_MAX_WIDTH = 80      # Max width untuk list biasa
LIST_DETAILED_MAX_WIDTH = 30   # Max width untuk list -a (detailed) 