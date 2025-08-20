#!/usr/bin/env python3
"""
Test Import Script untuk HPone

Script ini untuk test semua import dan identify issues.
"""

import sys
from pathlib import Path

print("🔍 TESTING IMPORTS...")
print("=" * 50)

# Test 1: Basic imports
print("\n📦 TEST 1: Basic Python imports")
try:
    import yaml
    print("✅ PyYAML: OK")
except ImportError as e:
    print(f"❌ PyYAML: {e}")

try:
    import subprocess
    print("✅ subprocess: OK")
except ImportError as e:
    print(f"❌ subprocess: {e}")

# Test 2: Core package
print("\n🔧 TEST 2: Core package")
try:
    from core import yaml
    print("✅ core.yaml: OK")
except ImportError as e:
    print(f"❌ core.yaml: {e}")

try:
    from core import docker
    print("✅ core.docker: OK")
except ImportError as e:
    print(f"❌ core.docker: {e}")

try:
    from core import config
    print("✅ core.config: OK")
except ImportError as e:
    print(f"❌ core.config: {e}")

try:
    from core import utils
    print("✅ core.utils: OK")
except ImportError as e:
    print(f"❌ core.utils: {e}")

# Test 3: Scripts package
print("\n📜 TEST 3: Scripts package")
try:
    from scripts import list
    print("✅ scripts.list: OK")
except ImportError as e:
    print(f"❌ scripts.list: {e}")

try:
    from scripts import inspect
    print("✅ scripts.inspect: OK")
except ImportError as e:
    print(f"❌ scripts.inspect: {e}")

try:
    from scripts import import_cmd
    print("✅ scripts.import_cmd: OK")
except ImportError as e:
    print(f"❌ scripts.import_cmd: {e}")

try:
    from scripts import check
    print("✅ scripts.check: OK")
except ImportError as e:
    print(f"❌ scripts.check: {e}")

# Test 4: Specific functions
print("\n🎯 TEST 4: Specific functions")
try:
    from core.yaml import load_tool_yaml_by_filename
    print("✅ load_tool_yaml_by_filename: OK")
except ImportError as e:
    print(f"❌ load_tool_yaml_by_filename: {e}")

try:
    from scripts.list import list_tools
    print("✅ list_tools: OK")
except ImportError as e:
    print(f"❌ list_tools: {e}")

try:
    from scripts.check import print_dependency_status
    print("✅ print_dependency_status: OK")
except ImportError as e:
    print(f"❌ print_dependency_status: {e}")

# Test 5: Constants
print("\n📋 TEST 5: Constants")
try:
    from core.constants import TOOLS_DIR
    print("✅ TOOLS_DIR: OK")
except ImportError as e:
    print(f"❌ TOOLS_DIR: {e}")

try:
    from core.constants import OUTPUT_DOCKER_DIR
    print("✅ OUTPUT_DOCKER_DIR: OK")
except ImportError as e:
    print(f"❌ OUTPUT_DOCKER_DIR: {e}")

print("\n" + "=" * 50)
print("🏁 IMPORT TEST SELESAI!")
