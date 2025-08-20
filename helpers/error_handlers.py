"""
Error Handlers untuk HPone

Fungsi-fungsi untuk handle error dengan lebih graceful dan user-friendly.
"""

import sys
from typing import Any, Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')


def handle_yaml_error(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator untuk handle YAML parsing errors."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            if "yaml" in str(e).lower():
                print("❌ ERROR: PyYAML tidak tersedia!")
                print("💡 Install dengan: pip install PyYAML")
                sys.exit(1)
            raise
        except Exception as e:
            if "yaml" in str(e).lower() or "yaml" in str(type(e).__name__).lower():
                print(f"❌ ERROR: Gagal parsing YAML: {e}")
                print("💡 Pastikan file YAML valid dan tidak ada syntax error")
                sys.exit(1)
            raise
    return wrapper


def handle_docker_error(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator untuk handle Docker command errors."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            if "docker" in str(e).lower():
                print("❌ ERROR: Docker tidak ditemukan!")
                print("💡 Install Docker terlebih dahulu")
                print("   Ubuntu/Debian: sudo apt install docker.io")
                print("   CentOS/RHEL: sudo yum install docker")
                print("   macOS: brew install docker")
                print("   Windows: Download dari https://docs.docker.com/desktop/")
                sys.exit(1)
            raise
        except Exception as e:
            if "docker" in str(e).lower():
                print(f"❌ ERROR: Gagal menjalankan Docker command: {e}")
                print("💡 Pastikan Docker service berjalan dan user punya permission")
                print("   Coba: sudo systemctl start docker")
                print("   Coba: sudo usermod -aG docker $USER")
                sys.exit(1)
            raise
    return wrapper


def safe_execute(func: Callable[..., T], 
                error_msg: str = "Terjadi error", 
                exit_on_error: bool = False) -> Optional[T]:
    """
    Execute function dengan error handling yang aman.
    
    Args:
        func: Function yang akan dijalankan
        error_msg: Pesan error yang akan ditampilkan
        exit_on_error: Apakah exit program jika terjadi error
    
    Returns:
        Result dari function atau None jika error
    """
    try:
        return func()
    except Exception as e:
        print(f"❌ {error_msg}: {e}")
        if exit_on_error:
            sys.exit(1)
        return None


def print_error_with_suggestion(error: Exception, 
                              suggestion: str = "", 
                              exit_code: int = 1) -> None:
    """
    Print error dengan suggestion yang helpful.
    
    Args:
        error: Exception yang terjadi
        suggestion: Suggestion untuk user
        exit_code: Exit code untuk program
    """
    print(f"❌ ERROR: {error}")
    if suggestion:
        print(f"💡 {suggestion}")
    
    if exit_code != 0:
        sys.exit(exit_code)


def check_file_permissions(file_path: str) -> bool:
    """
    Check apakah file bisa diakses.
    
    Args:
        file_path: Path ke file yang akan dicek
    
    Returns:
        True jika file bisa diakses, False jika tidak
    """
    try:
        with open(file_path, 'r') as f:
            f.read(1)
        return True
    except PermissionError:
        print(f"❌ ERROR: Tidak punya permission untuk akses file: {file_path}")
        print("💡 Coba jalankan dengan sudo atau check file permissions")
        return False
    except FileNotFoundError:
        print(f"❌ ERROR: File tidak ditemukan: {file_path}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Gagal akses file {file_path}: {e}")
        return False
