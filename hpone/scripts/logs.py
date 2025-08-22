#!/usr/bin/env python3
"""
Interactive logs viewer for HPone honeypot tools.

Provides functionality to:
1. View Docker container logs
2. Browse mounted data directories
3. View file contents with various options
"""

import subprocess
import sys
import platform
from pathlib import Path
from typing import Dict, List, Optional

try:
    import questionary
except ImportError:
    print("Error: questionary library not installed. Run: pip install questionary", file=sys.stderr)
    sys.exit(1)

from core.docker import is_tool_running
from core.utils import PREFIX_ERROR, PREFIX_WARN, PREFIX_OK


def show_docker_logs(tool_name: str, follow: bool = False) -> None:
    """Show Docker container logs."""
    try:
        if not is_tool_running(tool_name):
            print(f"{PREFIX_WARN} Container '{tool_name}' is not running")
            return

        cmd = ["docker", "logs"]
        if follow:
            cmd.append("-f")
        cmd.append(tool_name)

        print(f"📜 Docker logs for {tool_name}...")
        print("=" * 50)
        subprocess.run(cmd)

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to show Docker logs: {exc}", file=sys.stderr)


def parse_mounted_volumes(tool_name: str) -> List[Dict[str, Path]]:
    """Parse mounted volumes from Docker .env file."""
    try:
        from core.constants import OUTPUT_DOCKER_DIR

        # Read .env file from docker/<toolname>/.env
        env_file = OUTPUT_DOCKER_DIR / tool_name / ".env"
        if not env_file.exists():
            return []

        # Read all lines and create a dict of env vars
        env_vars = {}
        with env_file.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value

        data_mounts = []
        # Find all _VOL*_SRC entries
        for key, value in env_vars.items():
            if '_VOL' in key and key.endswith('_SRC'):
                local_path = Path(value)

                # Find corresponding _DST entry
                dst_key = key.replace('_SRC', '_DST')
                container_path = env_vars.get(dst_key, f"/opt/{tool_name}/{local_path.name}")

                data_mounts.append({
                    'name': f"{container_path} ← {local_path}",
                    'local_path': local_path,
                    'container_path': container_path,
                    'display_name': local_path.name if local_path.name else str(local_path)
                })

        return data_mounts

    except Exception as exc:
        # Don't print error - just return empty list
        return []


def get_file_view_command(action: str, file_path: Path) -> List[str]:
    """Get the appropriate command for file viewing based on platform."""
    is_windows = platform.system() == "Windows"

    if action == "head":
        if is_windows:
            # Use PowerShell Get-Content with -Head parameter
            return ["powershell", "-Command", f"Get-Content '{file_path}' -Head 50"]
        else:
            return ["head", "-50", str(file_path)]

    elif action == "cat":
        if is_windows:
            return ["type", str(file_path)]
        else:
            return ["cat", str(file_path)]

    elif action == "tail":
        if is_windows:
            return ["powershell", "-Command", f"Get-Content '{file_path}' -Tail 50"]
        else:
            return ["tail", "-f", str(file_path)]

    elif action == "grep":
        if is_windows:
            return ["findstr", "/n", str(file_path)]
        else:
            return ["grep", "-n", "--color=always", str(file_path)]

    return []
def view_file_content(file_path: Path) -> None:
    """Interactive file content viewer."""
    if not file_path.exists():
        print(f"{PREFIX_ERROR} File {file_path} does not exist")
        return

    if not file_path.is_file():
        print(f"{PREFIX_ERROR} {file_path} is not a file")
        return

    # Check file size
    file_size = file_path.stat().st_size
    size_mb = file_size / (1024 * 1024)

    choices = [
        '👀 Preview (first 50 lines)',
        '📜 View entire file',
        '🔍 Search in file',
        '🔙 Back'
    ]

    # Add tail -f option for log files (Linux/macOS only)
    if platform.system() != "Windows" and (any(ext in file_path.suffix.lower() for ext in ['.log', '.txt']) or 'log' in file_path.name.lower()):
        choices.insert(-1, '🔄 Follow (tail -f)')

    # Show file info
    print(f"\n📄 File: {file_path.name}")
    print(f"💾 Size: {size_mb:.2f} MB ({file_size:,} bytes)")
    print(f"📍 Path: {file_path}")

    action = questionary.select(
        "Choose action:",
        choices=choices
    ).ask()

    if not action or action.startswith('🔙'):
        return

    try:
        if action.startswith('👀'):
            print(f"\n📖 First 50 lines of {file_path.name}:")
            print("=" * 60)
            cmd = get_file_view_command("head", file_path)
            subprocess.run(cmd)

        elif action.startswith('📜'):
            if size_mb > 10:
                confirm = questionary.confirm(
                    f"File is {size_mb:.1f}MB. This might take a while. Continue?"
                ).ask()
                if not confirm:
                    return

            print(f"\n📖 Content of {file_path.name}:")
            print("=" * 60)
            cmd = get_file_view_command("cat", file_path)
            subprocess.run(cmd)

        elif action.startswith('🔄'):
            print(f"\n🔄 Following {file_path.name} (Ctrl+C to stop):")
            print("=" * 60)
            cmd = get_file_view_command("tail", file_path)
            subprocess.run(cmd)

        elif action.startswith('🔍'):
            search_term = questionary.text("Enter search term:").ask()
            if search_term:
                print(f"\n🔍 Searching for '{search_term}' in {file_path.name}:")
                print("=" * 60)
                if platform.system() == "Windows":
                    subprocess.run(["findstr", "/n", search_term, str(file_path)])
                else:
                    subprocess.run(["grep", "-n", "--color=always", search_term, str(file_path)])

    except KeyboardInterrupt:
        print(f"\n{PREFIX_OK} Stopped viewing file")
    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to view file: {exc}", file=sys.stderr)


def browse_directory(path: Path, tool_name: str) -> None:
    """Interactive directory browser."""
    current_path = path

    while True:
        if not current_path.exists():
            print(f"{PREFIX_ERROR} Directory {current_path} does not exist")
            return

        try:
            items = list(current_path.iterdir())
            dirs = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]

            # Sort directories and files separately
            dirs.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())

            choices = ['🔙 Back to main menu']

            # Add parent directory option if not at root
            if current_path != path:
                choices.append('⬆️  Parent directory')

            # Add directories
            for dir_item in dirs:
                choices.append(f"📁 {dir_item.name}/")

            # Add files
            for file_item in files:
                file_size = file_item.stat().st_size
                if file_size < 1024:
                    size_str = f"{file_size}B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size/1024:.1f}KB"
                else:
                    size_str = f"{file_size/(1024*1024):.1f}MB"
                choices.append(f"📄 {file_item.name} ({size_str})")

            if len(choices) == 1:  # Only "Back" option
                print(f"📂 {current_path} is empty")
                break

            # Show current path relative to data directory
            relative_path = current_path.relative_to(path) if current_path != path else "."
            selection = questionary.select(
                f"📂 {tool_name}/data/{relative_path}",
                choices=choices
            ).ask()

            if not selection or selection.startswith('🔙'):
                break
            elif selection.startswith('⬆️'):
                current_path = current_path.parent
            elif selection.startswith('📁'):
                # Navigate to subdirectory
                dirname = selection[2:-1]  # Remove emoji and trailing /
                current_path = current_path / dirname
            elif selection.startswith('📄'):
                # Extract filename (remove emoji and size info)
                filename = selection[2:].split(' (')[0]
                view_file_content(current_path / filename)

        except PermissionError:
            print(f"{PREFIX_ERROR} Permission denied accessing {current_path}")
            break
        except Exception as exc:
            print(f"{PREFIX_ERROR} Error browsing directory: {exc}", file=sys.stderr)
            break


def logs_main(tool_name: str) -> None:
    """Main logs command handler."""
    try:
        # Get mounted volumes from Docker .env file
        data_mounts = parse_mounted_volumes(tool_name)

        # Build main menu
        choices = []

        # Add Docker logs option
        if is_tool_running(tool_name):
            choices.extend([
                '🐳 Docker Logs (preview)',
                '🔄 Docker Logs (follow)'
            ])
        else:
            choices.append('🐳 Docker Logs (container not running)')

        # Add mounted directories
        for mount in data_mounts:
            if mount['local_path'].exists():
                try:
                    item_count = len(list(mount['local_path'].iterdir())) if mount['local_path'].is_dir() else 0
                    choices.append(f"📁 {mount['display_name']} ({item_count} items)")
                except PermissionError:
                    choices.append(f"📁 {mount['display_name']} (permission denied)")
            else:
                choices.append(f"📁 {mount['display_name']} (not found)")

        if len(choices) == 0:
            print(f"{PREFIX_WARN} No log sources available for {tool_name}")
            print(f"       Make sure the tool is imported: hpone up {tool_name}")
            return

        # Show main selection menu
        selection = questionary.select(
            f"🔍 Select log source for {tool_name}:",
            choices=choices
        ).ask()

        if not selection:
            return

        # Handle selection
        if selection.startswith('🐳'):
            if 'not running' in selection:
                print(f"{PREFIX_WARN} Container '{tool_name}' is not running")
            elif 'follow' in selection:
                show_docker_logs(tool_name, follow=True)
            else:
                show_docker_logs(tool_name, follow=False)

        elif selection.startswith('📁'):
            # Find corresponding mount
            display_name = selection.split(' (')[0][2:]  # Remove emoji and item count
            mount = next((m for m in data_mounts if m['display_name'] == display_name), None)

            if mount and mount['local_path'].exists():
                browse_directory(mount['local_path'], tool_name)
            else:
                print(f"{PREFIX_ERROR} Directory not found or inaccessible")

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to show logs: {exc}", file=sys.stderr)
