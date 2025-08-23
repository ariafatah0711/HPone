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
                print("💡 Install with: pip install PyYAML")
                sys.exit(1)
            raise
        except Exception as e:
            if "yaml" in str(e).lower() or "yaml" in str(type(e).__name__).lower():
                print(f"{PREFIX_ERROR} Failed to parse YAML: {e}")
                print("💡 Make sure the YAML file is valid and contains no syntax errors")
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
                print("💡 Please install Docker first")
                print("   Ubuntu/Debian: sudo apt install docker.io")
                print("   CentOS/RHEL: sudo yum install docker")
                print("   macOS: brew install docker")
                print("   Windows: Download from https://docs.docker.com/desktop/")
                sys.exit(1)
            raise
        except Exception as e:
            if "docker" in str(e).lower():
                print(f"{PREFIX_ERROR} Failed to run Docker command: {e}")
                print("💡 Ensure Docker service is running and the user has permissions")
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
        print(f"💡 {suggestion}")

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
        print(f"❌ ERROR: Permission denied for file: {file_path}")
        print("💡 Try running with sudo or check file permissions")
        return False
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to access file {file_path}: {e}")
        return False
