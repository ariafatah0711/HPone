#!/usr/bin/env python3
"""
HPone Configuration File

This file contains path configurations that can be modified by users.
"""

from pathlib import Path

# Project root directory location (folder where this file is located)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Behavior configuration
ALWAYS_IMPORT = True          # True: hide import/remove commands, auto-import on up

# Honeypots directory location (contains YAML honeypot files)
HONEYPOT_MANIFEST_DIR = PROJECT_ROOT / "honeypots"
# Docker template directory location
TEMPLATE_DOCKER_DIR = PROJECT_ROOT / "template" / "docker"
# Docker output directory location (import results location)
OUTPUT_DOCKER_DIR = PROJECT_ROOT / "docker"
# Data directory location for mount (only deleted when clean --data)
DATA_DIR = PROJECT_ROOT / "data"

# Configuration for list command
LIST_BASIC_MAX_WIDTH = 80      # Max width for basic list
LIST_DETAILED_MAX_WIDTH = 30   # Max width for list -a (detailed)

# Configuration for status command
STATUS_TABLE_MAX_WIDTH = 40    # Max width for status table columns

# Logging configuration
USE_EPHEMERAL_LOGGING = True  # True: use ephemeral logging for up/down commands, False: use simple output
