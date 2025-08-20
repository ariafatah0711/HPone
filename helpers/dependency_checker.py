"""
Dependency Checker untuk HPone

Fungsi-fungsi untuk mengecek apakah semua dependencies yang dibutuhkan tersedia.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Dict


def check_python_dependencies() -> Dict[str, bool]:
    """Check Python package dependencies."""
    dependencies = {
        'PyYAML': False,
        'pathlib': True,  # Built-in di Python 3.4+
        'typing': True,   # Built-in di Python 3.5+
    }
    
    # Check PyYAML
    try:
        import yaml
        dependencies['PyYAML'] = True
    except ImportError:
        pass
    
    return dependencies


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
    """Check semua dependencies dan return status dan detail."""
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
    """Print status dependencies dengan format yang rapi."""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                           🔍 CHECKING DEPENDENCIES                           ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    
    ok, deps = check_all_dependencies()
    
    # Python dependencies
    print(f"\n🐍 PYTHON")
    print("   ┌─────────────────────────────────────────────────────────────────────────┐")
    for dep, available in deps['python'].items():
        status = "✅ OK" if available else "❌ MISSING"
        print(f"   │ {dep:<15} : {status:<52} │")
    print("   └─────────────────────────────────────────────────────────────────────────┘")
    
    # System dependencies
    print(f"\n🖥️  SYSTEM")
    print("   ┌─────────────────────────────────────────────────────────────────────────┐")
    for dep, available in deps['system'].items():
        status = "✅ OK" if available else "❌ MISSING"
        print(f"   │ {dep:<15} : {status:<52} │")
    print("   └─────────────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "═" * 80)
    
    if ok:
        print("🎉 READY!")
    else:
        print("⚠️  MISSING DEPENDENCIES!")
    
    return ok


def get_installation_instructions() -> str:
    """Return installation instructions untuk dependencies yang kurang."""
    instructions = []
    
    ok, deps = check_all_dependencies()
    
    if not deps['python']['PyYAML']:
        instructions.append("📦 PYTHON: pip install PyYAML")
    
    if not any(deps['system'].values()):
        instructions.append("🐳 DOCKER:")
        instructions.append("   Ubuntu/Debian: sudo apt install docker.io docker-compose")
        instructions.append("   CentOS/RHEL: sudo yum install docker docker-compose")
        instructions.append("   macOS: brew install docker docker-compose")
        instructions.append("   Windows: https://docs.docker.com/desktop/")
    
    if instructions:
        return "\n".join(instructions)
    else:
        return "✅ READY!"


def require_dependencies() -> None:
    """Check dependencies dan exit jika ada yang kurang."""
    ok, deps = check_all_dependencies()
    
    if not ok:
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                           ❌ MISSING DEPENDENCIES                            ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print_dependency_status()
        print("\n📋 INSTALL:")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        install_text = get_installation_instructions()
        for line in install_text.strip().split('\n'):
            if line.strip():
                print(f"   │ {line.strip():<65} │")
        print("   └─────────────────────────────────────────────────────────────────────────┘")
        sys.exit(1)
