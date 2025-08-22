"""
Dependency checker for HPone.

Functions to verify that required dependencies are available.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict

def check_python_dependencies() -> Dict[str, bool]:
    """Check Python package dependencies."""
    builtin = {"pathlib": True, "typing": True}  # built-ins
    to_check = ["yaml", "questionary"]           # external packages

    deps = builtin.copy()
    for module in to_check:
        try:
            __import__(module)
            # tampilkan dengan nama lebih enak (PyYAML, bukan yaml)
            deps["PyYAML" if module == "yaml" else module] = True
        except ImportError:
            deps["PyYAML" if module == "yaml" else module] = False

    return deps

def check_system_dependencies() -> Dict[str, bool]:
    """Check system command dependencies."""
    dependencies = {
        'docker': False,
        'docker-compose': False,
        'docker compose': False,  # Docker Compose v2
    }

    # Check docker command
    try:
        result = subprocess.run(['docker', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            dependencies['docker'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass

    # Check docker-compose v1
    try:
        result = subprocess.run(['docker-compose', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            dependencies['docker-compose'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass

    # Check docker compose v2
    try:
        result = subprocess.run(['docker', 'compose', 'version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            dependencies['docker compose'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass

    return dependencies


def check_all_dependencies() -> Tuple[bool, Dict[str, Dict[str, bool]]]:
    """Check all dependencies and return status and details."""
    python_deps = check_python_dependencies()
    system_deps = check_system_dependencies()

    all_deps = {
        'python': python_deps,
        'system': system_deps
    }

    # Check if critical dependencies are available
    critical_python = all(python_deps.values())
    critical_system = any([system_deps['docker'], system_deps['docker-compose'], system_deps['docker compose']])

    all_ok = critical_python and critical_system

    return all_ok, all_deps


def print_dependency_status() -> None:
    """Print dependency status in a clean format."""
    print("🔍 Checking dependencies...")

    ok, deps = check_all_dependencies()

    # Python dependencies
    print("\n🐍 Python packages:")
    for dep, available in deps['python'].items():
        status = "✅" if available else "❌"
        print(f"   {status} {dep}")

    # System dependencies
    print("\n🐳 Docker:")
    docker_ok = deps['system']['docker']
    compose_v1_ok = deps['system']['docker-compose']
    compose_v2_ok = deps['system']['docker compose']

    print(f"   {'✅' if docker_ok else '❌'} docker")
    if compose_v2_ok:
        print("   ✅ docker compose (v2)")
    elif compose_v1_ok:
        print("   ✅ docker-compose (v1)")
    else:
        print("   ❌ docker compose")

    print(f"\n{'🎉 Ready to go!' if ok else '⚠️  Some dependencies missing'}")
    return ok


def get_installation_instructions() -> str:
    """Return installation instructions for missing dependencies."""
    instructions = []
    ok, deps = check_all_dependencies()

    # Check Python packages
    missing_python = [pkg for pkg, available in deps['python'].items() if not available]
    if missing_python:
        instructions.append(f"📦 Install Python packages: pip install {' '.join(missing_python)}")

    # Check Docker
    if not any(deps['system'].values()):
        instructions.append("🐳 Install Docker: https://docs.docker.com/get-docker/")

    return "\n".join(instructions) if instructions else "✅ All dependencies satisfied!"


def require_dependencies() -> None:
    """Check dependencies and exit if any are missing."""
    ok, deps = check_all_dependencies()

    if not ok:
        print("❌ Missing dependencies!")
        print_dependency_status()
        print("\n📋 To install missing dependencies:")
        instructions = get_installation_instructions()
        for line in instructions.split('\n'):
            if line.strip():
                print(f"   {line.strip()}")
        print()
        sys.exit(1)
