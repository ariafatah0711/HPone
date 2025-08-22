"""
Docker helpers for HPone.

Functions to start and stop Docker containers.
"""

import subprocess
from pathlib import Path
from typing import List, Optional

# Import constants dan functions dari helpers
from .constants import OUTPUT_DOCKER_DIR
from .utils import PREFIX_OK, PREFIX_WARN, COLOR_YELLOW, COLOR_RESET
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

def run_compose_action(tool_dir: Path, action: str, extra_args: Optional[List[str]] = None) -> None:
    if not (tool_dir / "docker-compose.yml").exists():
        raise FileNotFoundError(f"docker-compose.yml not found in {tool_dir}")

    # Check if ephemeral logging is enabled
    try:
        from config import USE_EPHEMERAL_LOGGING
    except ImportError:
        USE_EPHEMERAL_LOGGING = True  # Default to True if config not found

    # Use ephemeral logging when enabled (even with extra args)
    if USE_EPHEMERAL_LOGGING:
        # Use ephemeral logging for better UX
        from .log_runner import run_docker_compose_action_with_args

        # Extract tool name from directory
        tool_name = tool_dir.name

        success, duration = run_docker_compose_action_with_args(action, tool_name, tool_dir, extra_args)

        if not success:
            raise subprocess.CalledProcessError(1, f"docker compose {action}")
    else:
        # Use simple output (original behavior)
        cmd_dc = ["docker", "compose", action]
        if action == "up":
            cmd_dc.append("-d")
        if extra_args:
            cmd_dc.extend(extra_args)

        try:
            subprocess.run(
                cmd_dc,
                cwd=str(tool_dir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            return
        except FileNotFoundError:
            # Fallback ke docker-compose v1
            cmd_legacy = ["docker-compose", action]
            if action == "up":
                cmd_legacy.append("-d")
            if extra_args:
                cmd_legacy.extend(extra_args)
            subprocess.run(
                cmd_legacy,
                cwd=str(tool_dir),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )


def up_tool(tool_id: str, force: bool = False) -> None:
    # Import di dalam function untuk avoid circular import
    from scripts.list import resolve_tool_dir_id
    dir_id = resolve_tool_dir_id(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / dir_id
    if not dest_dir.exists():
        raise FileNotFoundError(f"Docker folder for tool '{tool_id}' not found: {dest_dir}. Run 'import' first.")

    # Check if tool is enabled (unless force is used)
    if not force:
        from .yaml import is_tool_enabled
        if not is_tool_enabled(tool_id):
            raise ValueError(f"Tool '{tool_id}' is not enabled. Run 'enable {tool_id}' first or use --force.")

    run_compose_action(dest_dir, "up")

    # Show output based on logging mode
    try:
        from config import USE_EPHEMERAL_LOGGING
    except ImportError:
        USE_EPHEMERAL_LOGGING = True

    if not USE_EPHEMERAL_LOGGING:
        print(f"{COLOR_YELLOW}[UP]{COLOR_RESET} {dir_id} {PREFIX_OK}")


def down_tool(tool_id: str, remove_volumes: bool = False, remove_images: bool = False) -> None:
    # Import di dalam function untuk avoid circular import
    from scripts.list import resolve_tool_dir_id
    dir_id = resolve_tool_dir_id(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / dir_id
    if not dest_dir.exists():
        print(f"{PREFIX_WARN} Skip {dir_id}: folder not found.")
        return
    extra_args: List[str] = []
    if remove_volumes:
        extra_args.append("-v")
    if remove_images:
        extra_args.extend(["--rmi", "local"])
    run_compose_action(dest_dir, "down", extra_args=extra_args if extra_args else None)

    # Show output based on logging mode
    try:
        from config import USE_EPHEMERAL_LOGGING
    except ImportError:
        USE_EPHEMERAL_LOGGING = True

    if not USE_EPHEMERAL_LOGGING:
        print(f"{COLOR_YELLOW}[DOWN]{COLOR_RESET} {dir_id} {PREFIX_OK}")


def shell_tool(tool_id: str) -> None:
    """Open shell (bash/sh) in running container."""
    # Import di dalam function untuk avoid circular import
    from scripts.list import resolve_tool_dir_id
    dir_id = resolve_tool_dir_id(tool_id)
    dest_dir = OUTPUT_DOCKER_DIR / dir_id
    if not dest_dir.exists():
        raise FileNotFoundError(f"Docker folder for tool '{tool_id}' not found: {dest_dir}. Run 'import' first.")

    # Check if container is running
    if not is_tool_running(tool_id):
        raise RuntimeError(f"Tool '{tool_id}' is not running. Start it first with 'up {tool_id}'.")

    # Get the service name (usually same as tool_id, but could be different)
    # For now, assume it's the same as tool_id
    service_name = tool_id

    # Try bash first, then fallback to sh
    shells_to_try = ["bash", "sh"]

    for shell in shells_to_try:
        try:
            cmd = ["docker", "compose", "exec", service_name, shell]
            subprocess.run(cmd, cwd=str(dest_dir), check=True)
            return  # Success, exit function
        except FileNotFoundError:
            # Fallback to docker-compose v1
            try:
                cmd_legacy = ["docker-compose", "exec", service_name, shell]
                subprocess.run(cmd_legacy, cwd=str(dest_dir), check=True)
                return  # Success, exit function
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue  # Try next shell
        except subprocess.CalledProcessError:
            continue  # Try next shell

    # If we get here, neither bash nor sh worked
    raise RuntimeError(f"Could not open shell in container '{tool_id}'. Neither bash nor sh are available.")
