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
    """Show Docker container logs simply."""
    try:
        if not is_tool_running(tool_name):
            print(f"{PREFIX_WARN} Container '{tool_name}' is not running")
            return

        if follow:
            # Simple follow mode
            print(f"🔄 Following logs for {tool_name} (Ctrl+C to stop)")
            print("=" * 60)

            cmd = ["docker", "logs", "-f", "--tail", "20", tool_name]

            try:
                subprocess.run(cmd)
            except KeyboardInterrupt:
                print(f"\n{PREFIX_OK} Stopped following logs")

        else:
            # Show recent logs simply
            print(f"📜 Recent logs for {tool_name}")
            print("=" * 60)

            cmd = ["docker", "logs", "--tail", "30", tool_name]
            subprocess.run(cmd)
            print("=" * 60)

    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to show logs: {exc}", file=sys.stderr)


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

                # Only add directories, not individual files
                if local_path.exists() and local_path.is_dir():
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
        '📜 View entire file',
        '🔍 Search in file',
        '🔙 Back'
    ]

    while True:  # Loop until user chooses to go back
        action = questionary.select(
            f"📄 {file_path.name} ({size_mb:.2f} MB)",
            choices=choices
        ).unsafe_ask()

        if not action or action.startswith('🔙'):
            return  # Go back to directory

        try:
            if action.startswith('📜'):
                if file_size == 0:
                    print("📖 File is empty")
                    return  # Return immediately after showing empty file

                if size_mb > 10:
                    confirm = questionary.confirm(
                        f"File is {size_mb:.1f}MB. Continue?"
                    ).unsafe_ask()
                    if not confirm:
                        continue

                print("📖 Full content:")
                print("=" * 50)
                cmd = get_file_view_command("cat", file_path)
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.stdout.strip():
                    print(result.stdout.rstrip())
                else:
                    print("(File is empty or contains only whitespace)")
                print("=" * 50)
                return  # Return immediately after showing file content

            elif action.startswith('🔍'):
                if file_size == 0:
                    print("🔍 Cannot search in empty file")
                    continue

                search_term = questionary.text("Search term:").unsafe_ask()
                if search_term:
                    print(f"🔍 Results for '{search_term}':")
                    print("=" * 50)
                    if platform.system() == "Windows":
                        result = subprocess.run(["findstr", "/n", search_term, str(file_path)], capture_output=True, text=True)
                    else:
                        result = subprocess.run(["grep", "-n", "--color=always", search_term, str(file_path)], capture_output=True, text=True)

                    if result.stdout.strip():
                        print(result.stdout.rstrip())
                    else:
                        print(f"No matches found for '{search_term}'")
                    print("=" * 50)
                    # Continue loop to allow more searches

        except KeyboardInterrupt:
            print(f"\n{PREFIX_OK} Stopped")
        except Exception as exc:
            print(f"{PREFIX_ERROR} Error: {exc}", file=sys.stderr)


def browse_directory(path: Path, tool_name: str) -> bool:
    """Interactive directory browser with proper navigation.

    Returns:
        bool: True if should return to main menu, False if should exit completely
    """

    def browse_level(current_path: Path, is_root: bool = True) -> bool:
        """Browse a single directory level.

        Returns:
            bool: True if should return to main menu, False if should exit completely
        """
        if not current_path.exists():
            print(f"{PREFIX_ERROR} Directory {current_path} does not exist")
            return False

        try:
            items = list(current_path.iterdir())
            dirs = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]

            # Sort directories and files separately
            dirs.sort(key=lambda x: x.name.lower())
            files.sort(key=lambda x: x.name.lower())

            choices = []

            # Add back option based on context
            if is_root:
                choices.append('🔙 Back to main menu')
            else:
                choices.append('⬆️  Parent directory')

            # Add directories
            for dir_item in dirs:
                choices.append(f"📁 {dir_item.name}/")

            # Add files (skip empty files)
            for file_item in files:
                file_size = file_item.stat().st_size
                if file_size == 0:
                    # Skip empty files - don't add them to choices
                    continue
                elif file_size < 1024:
                    size_str = f"{file_size}B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size/1024:.1f}KB"
                else:
                    size_str = f"{file_size/(1024*1024):.1f}MB"
                choices.append(f"📄 {file_item.name} ({size_str})")

            # Show directory info
            total_files = len(files)
            non_empty_files = len([f for f in files if f.stat().st_size > 0])
            empty_files = total_files - non_empty_files

            if len(choices) == 1:  # Only back option (empty directory)
                if total_files == 0:
                    info_msg = "Directory is empty"
                else:
                    info_msg = f"Directory contains {empty_files} empty file(s) - no viewable content"
                print(f"📂 {info_msg}")
                # Automatically return to main menu for empty directories
                return True if is_root else False

            # Show current path relative to data directory
            relative_path = current_path.relative_to(path) if current_path != path else "."
            path_display = f"{tool_name}/data/{relative_path}" if relative_path != "." else f"{tool_name}/data"

            while True:
                selection = questionary.select(
                    f"📂 {path_display}",
                    choices=choices
                ).unsafe_ask()

                if not selection:
                    return False
                elif selection.startswith('🔙'):
                    return True  # Back to main menu
                elif selection.startswith('⬆️'):
                    return False  # Go back to parent (handled by recursion)
                elif selection.startswith('📁'):
                    # Navigate to subdirectory
                    dirname = selection[2:-1]  # Remove emoji and trailing /
                    subdir_path = current_path / dirname
                    result = browse_level(subdir_path, is_root=False)
                    if result:  # If subdirectory returned "back to main menu"
                        return True
                    # Otherwise continue in current menu
                elif selection.startswith('📄'):
                    # Extract filename (remove emoji and size info)
                    filename = selection[2:].split(' (')[0]
                    view_file_content(current_path / filename)
                    # After viewing file, stay in current menu

        except PermissionError:
            print(f"{PREFIX_ERROR} Permission denied accessing {current_path}")
            return False
        except Exception as exc:
            print(f"{PREFIX_ERROR} Error browsing directory: {exc}", file=sys.stderr)
            return False

    # Start browsing from the root level
    return browse_level(path, is_root=True)


def logs_main(tool_name: str) -> None:
    """Main logs command handler."""
    try:
        while True:  # Loop to allow returning to main menu
            # Get mounted volumes from Docker .env file
            data_mounts = parse_mounted_volumes(tool_name)

            # Build main menu
            choices = []

            # Add Docker logs options
            if is_tool_running(tool_name):
                choices.extend([
                    '📜 Recent logs',
                    '🔄 Follow live logs'
                ])
            else:
                choices.append('❌ Container not running')

            # Add data directories (only directories, not files)
            if data_mounts:
                choices.append('---')  # Separator
                for mount in data_mounts:
                    if mount['local_path'].exists():
                        try:
                            items = list(mount['local_path'].iterdir())
                            files = [item for item in items if item.is_file()]
                            non_empty_files = [f for f in files if f.stat().st_size > 0]
                            item_count = len(non_empty_files)

                            if item_count > 0:
                                choices.append(f"📁 Browse {mount['display_name']} ({item_count} files)")
                            else:
                                total_files = len(files)
                                if total_files > 0:
                                    choices.append(f"📁 Browse {mount['display_name']} ({total_files} empty files)")
                                else:
                                    choices.append(f"📁 Browse {mount['display_name']} (empty)")
                        except PermissionError:
                            choices.append(f"📁 Browse {mount['display_name']} (access denied)")
                    else:
                        choices.append(f"📁 Browse {mount['display_name']} (not found)")

            if len([c for c in choices if c != '---' and not c.startswith('❌')]) == 0:
                print(f"{PREFIX_WARN} No log sources available for {tool_name}")
                print(f"       Make sure the tool is running: hpone up {tool_name}")
                return

            # Show main selection menu
            selection = questionary.select(
                f"🔍 Logs for {tool_name}:",
                choices=[c for c in choices if c != '---']  # Remove separator
            ).unsafe_ask()

            if not selection:
                return

            # Handle selection
            if selection.startswith('📜'):
                show_docker_logs(tool_name, follow=False)
                # After showing logs, return to main menu
            elif selection.startswith('🔄'):
                show_docker_logs(tool_name, follow=True)
                # After following logs, return to main menu
            elif selection.startswith('❌'):
                print(f"{PREFIX_WARN} Container '{tool_name}' is not running")
                print(f"       Start it with: hpone up {tool_name}")
                # Return to main menu
            elif selection.startswith('📁'):
                # Extract directory name from selection
                # Format: "📁 Browse dirname (X files)"
                parts = selection.split(' ')
                if len(parts) >= 3:
                    dir_name = parts[2]  # Get the directory name
                    mount = next((m for m in data_mounts if m['display_name'] == dir_name), None)

                    if mount and mount['local_path'].exists():
                        should_return_to_menu = browse_directory(mount['local_path'], tool_name)
                        if not should_return_to_menu:
                            return  # User wants to exit completely
                        # If should_return_to_menu is True, continue the loop to show main menu again
                    else:
                        print(f"{PREFIX_ERROR} Directory not found or inaccessible")
                        # Return to main menu

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully at the top level
        return
    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to show logs: {exc}", file=sys.stderr)
