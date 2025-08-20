"""
Docker Helpers untuk HPone

Fungsi-fungsi untuk menjalankan dan menghentikan Docker containers.
"""

import subprocess
from pathlib import Path
from typing import List

# Import constants dan functions dari helpers
from .constants import OUTPUT_DOCKER_DIR
# Import di dalam function untuk avoid circular import

def is_tool_running(tool_id: str) -> bool:
    """Check if tool is running by checking Docker container status."""
    try:
        # Import di dalam function untuk avoid circular import
        from scripts.list import resolve_tool_dir_id
        dir_id = resolve_tool_dir_id(tool_id)
        dest_dir = OUTPUT_DOCKER_DIR / dir_id
        if not dest_dir.exists():
            return False

        # Check if any containers for this tool are running
        cmd = ["docker", "compose", "ps", "--format", "json"]
        try:
            result = subprocess.run(cmd, cwd=str(dest_dir), capture_output=True, text=True, check=True)
            # If output is not empty and contains running containers
            if result.stdout.strip():
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to docker-compose v1
            try:
                cmd_legacy = ["docker-compose", "ps", "--format", "json"]
                result = subprocess.run(cmd_legacy, cwd=str(dest_dir), capture_output=True, text=True, check=True)
                if result.stdout.strip():
                    return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        return False
    except Exception:
        return False


def run_compose_action(tool_dir: Path, action: str) -> None:
    if not (tool_dir / "docker-compose.yml").exists():
        raise FileNotFoundError(f"docker-compose.yml tidak ditemukan di {tool_dir}")

    cmd_dc = ["docker", "compose", action]
    if action == "up":
        cmd_dc.append("-d")

    try:
        subprocess.run(cmd_dc, cwd=str(tool_dir), check=True)
        return
    except FileNotFoundError:
        # Fallback ke docker-compose v1
        cmd_legacy = ["docker-compose", action]
        if action == "up":
            cmd_legacy.append("-d")
        subprocess.run(cmd_legacy, cwd=str(tool_dir), check=True)


def up_tool(tool_id: str, force: bool = False) -> None:
    # Import di dalam function untuk avoid circular import
    from scripts.list import resolve_tool_dir_id
    dir_id = resolve_tool_dir_id(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / dir_id
    if not dest_dir.exists():
        raise FileNotFoundError(f"Folder docker untuk tool '{tool_id}' tidak ditemukan: {dest_dir}. Jalankan 'import' terlebih dahulu.")

    # Check if tool is enabled (unless force is used)
    if not force:
        from .yaml import is_tool_enabled
        if not is_tool_enabled(tool_id):
            raise ValueError(f"Tool '{tool_id}' tidak enabled. Jalankan 'enable {tool_id}' terlebih dahulu atau gunakan --force.")

    print(f"[UP] {dir_id} ...", flush=True)
    run_compose_action(dest_dir, "up")
    print(f"[UP] {dir_id} OK")


def down_tool(tool_id: str) -> None:
    # Import di dalam function untuk avoid circular import
    from scripts.list import resolve_tool_dir_id
    dir_id = resolve_tool_dir_id(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / dir_id
    if not dest_dir.exists():
        print(f"[DOWN] Skip {dir_id}: folder tidak ada.")
        return
    print(f"[DOWN] {dir_id} ...", flush=True)
    run_compose_action(dest_dir, "down")
    print(f"[DOWN] {dir_id} OK")
