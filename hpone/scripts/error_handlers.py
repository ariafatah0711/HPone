"""
Error handlers for HPone.

Helpers to handle errors more gracefully and user-friendly.
"""

import sys
from typing import Any, Callable, TypeVar, Optional
from functools import wraps
from core.utils import PREFIX_ERROR

T = TypeVar('T')


def handle_yaml_error(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle YAML parsing errors."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            if "yaml" in str(e).lower():
                print(f"{PREFIX_ERROR} PyYAML is not available!")
                print("   Install with: pip install PyYAML")
                sys.exit(1)
            raise
        except Exception as e:
            if "yaml" in str(e).lower() or "yaml" in str(type(e).__name__).lower():
                print(f"{PREFIX_ERROR} Failed to parse YAML: {e}")
                print("   Make sure the YAML file is valid and contains no syntax errors")
                sys.exit(1)
            raise
    return wrapper


def handle_docker_error(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle Docker command errors."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            if "docker" in str(e).lower():
                print(f"{PREFIX_ERROR} Docker not found!")
                print("   Please install Docker first")
                print("   Ubuntu/Debian: sudo apt install docker.io")
                print("   CentOS/RHEL: sudo yum install docker")
                print("   macOS: brew install docker")
                print("   Windows: Download from https://docs.docker.com/desktop/")
                sys.exit(1)
            raise
        except Exception as e:
            if "docker" in str(e).lower():
                print(f"{PREFIX_ERROR} Failed to run Docker command: {e}")
                print("   Ensure Docker service is running and the user has permissions")
                print("   Try: sudo systemctl start docker")
                print("   Try: sudo usermod -aG docker $USER")
                sys.exit(1)
            raise
    return wrapper


def safe_execute(func: Callable[..., T],
                error_msg: str = "An error occurred",
                exit_on_error: bool = False) -> Optional[T]:
    """
    Execute a function with safe error handling.

    Args:
        func: Function to execute
        error_msg: Error message to display
        exit_on_error: Whether to exit program on error

    Returns:
        Result dari function atau None jika error
    """
    try:
        return func()
    except Exception as e:
        print(f"{PREFIX_ERROR} {error_msg}: {e}")
        if exit_on_error:
            sys.exit(1)
        return None


def print_error_with_suggestion(error: Exception,
                              suggestion: str = "",
                              exit_code: int = 1) -> None:
    """
    Print an error along with a helpful suggestion.

    Args:
        error: The exception raised
        suggestion: Helpful suggestion for the user
        exit_code: Program exit code
    """
    print(f"{PREFIX_ERROR} {error}")
    if suggestion:
        print(f"   {suggestion}")

    if exit_code != 0:
        sys.exit(exit_code)


def check_file_permissions(file_path: str) -> bool:
    """
    Check whether a file can be accessed.

    Args:
        file_path: Path to the file to check

    Returns:
        True if file is accessible, False otherwise
    """
    try:
        with open(file_path, 'r') as f:
            f.read(1)
        return True
    except PermissionError:
        print(f"{PREFIX_ERROR} Permission denied for file: {file_path}")
        print("   Try running with sudo or check file permissions")
        return False
    except FileNotFoundError:
        print(f"{PREFIX_ERROR} File not found: {file_path}")
        return False
    except Exception as e:
        print(f"{PREFIX_ERROR} Failed to access file {file_path}: {e}")
        return False


def check_docker_permissions() -> bool:
    """Check if Docker is accessible and user has proper permissions."""
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return True

        # Handle common Docker errors
        error_output = result.stderr.lower()
        if "permission denied" in error_output:
            print(f"{PREFIX_ERROR} Docker permission denied!")
            print("   Fix: Add your user to the docker group: sudo usermod -aG docker $USER")
            print("   Then restart your shell")
        elif "cannot connect" in error_output:
            print(f"{PREFIX_ERROR} Docker service is not running!")
            print("   Start Docker service: sudo systemctl start docker")
        else:
            print(f"{PREFIX_ERROR} Docker command failed: {result.stderr}")
        return False

    except FileNotFoundError:
        print(f"{PREFIX_ERROR} Docker not found! Please install Docker first.")
        return False
    except subprocess.TimeoutExpired:
        print(f"{PREFIX_ERROR} Docker command timed out! Try restarting Docker.")
        return False
    except Exception as e:
        print(f"{PREFIX_ERROR} Docker check failed: {e}")
        return False


def check_directory_permissions(dir_path: str) -> bool:
    """Check if directory is accessible and writable."""
    import os
    from pathlib import Path

    try:
        path = Path(dir_path)

        if not path.exists() or not path.is_dir():
            return False

        return os.access(path, os.R_OK | os.W_OK)

    except Exception:
        return False


def auto_fix_permissions() -> bool:
    """Automatically fix HPone directory permissions if possible."""
    import subprocess
    import os
    from pathlib import Path

    try:
        # Flexible path detection for different installation types
        hpone_base = None

        # Check if we're in a .deb package installation
        if Path("/opt/hpone").exists():
            hpone_base = Path("/opt/hpone")
        else:
            # Fallback to script location for development/manual installs
            # Go up from hpone/scripts/error_handlers.py to project root
            script_dir = Path(__file__).resolve().parent.parent.parent
            if (script_dir / "app.py").exists():
                hpone_base = script_dir

        if not hpone_base or not hpone_base.exists():
            return False  # Cannot determine HPone installation path

        # Directories that need permission fixing
        target_dirs = []
        for dirname in ["docker", "conf", "honeypots", "data"]:
            dir_path = hpone_base / dirname
            if dir_path.exists():
                target_dirs.append((dirname, dir_path))

        if not target_dirs:
            return True  # Nothing to fix

        # Check if user is in docker group or has sudo access
        in_docker_group = False
        can_sudo = False

        try:
            result = subprocess.run(["groups"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and "docker" in result.stdout:
                in_docker_group = True
        except Exception:
            pass

        try:
            result = subprocess.run(["sudo", "-n", "true"], capture_output=True, timeout=5)
            if result.returncode == 0:
                can_sudo = True
        except Exception:
            pass

        if not in_docker_group and not can_sudo:
            return False  # Cannot fix permissions

        # Fix permissions for each directory
        for dirname, dir_path in target_dirs:
            try:
                if dirname == "data":
                    # Data directory needs world-writable permissions for containers
                    dir_perm = "2777"
                    file_perm = "666"
                else:
                    # Other directories use group-writable permissions
                    dir_perm = "2775"
                    file_perm = "664"

                if in_docker_group:
                    # Fix without sudo
                    subprocess.run(["find", str(dir_path), "-type", "d", "-exec", "chmod", dir_perm, "{}", ";"],
                                 capture_output=True, timeout=10)
                    subprocess.run(["find", str(dir_path), "-type", "f", "-exec", "chmod", file_perm, "{}", ";"],
                                 capture_output=True, timeout=10)
                    subprocess.run(["chgrp", "-R", "docker", str(dir_path)],
                                 capture_output=True, timeout=10)
                elif can_sudo:
                    # Fix with sudo
                    subprocess.run(["sudo", "find", str(dir_path), "-type", "d", "-exec", "chmod", dir_perm, "{}", ";"],
                                 capture_output=True, timeout=10)
                    subprocess.run(["sudo", "find", str(dir_path), "-type", "f", "-exec", "chmod", file_perm, "{}", ";"],
                                 capture_output=True, timeout=10)
                    subprocess.run(["sudo", "chgrp", "-R", "docker", str(dir_path)],
                                 capture_output=True, timeout=10)

            except Exception:
                # Silently continue if fixing one directory fails
                continue

        return True

    except Exception:
        return False
