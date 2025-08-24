#!/usr/bin/env python3
"""
Edit command implementation for HPone.

Provides functionality to edit honeypot configurations and system files
using the user's preferred editor with automatic validation.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

# Local imports to avoid circular dependencies
def get_error_handlers():
    """Get error handlers with local import to avoid circular dependencies."""
    try:
        from . import handle_docker_error
        return handle_docker_error
    except ImportError:
        # Fallback: no error handling decorator
        def dummy_decorator(func):
            return func
        return dummy_decorator

def get_yaml_validator():
    """Get YAML validation function with local import."""
    try:
        from core.yaml import load_honeypot_yaml_by_filename
        return load_honeypot_yaml_by_filename
    except ImportError:
        return None

def get_project_paths():
    """Get project paths with local import."""
    try:
        from core.constants import PROJECT_ROOT, HONEYPOT_MANIFEST_DIR
        return PROJECT_ROOT, HONEYPOT_MANIFEST_DIR
    except ImportError:
        # Fallback to relative paths
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        honeypot_dir = project_root / "honeypots"
        return project_root, honeypot_dir

def get_utils():
    """Get utility functions with local import."""
    try:
        from core.utils import PREFIX_OK, PREFIX_ERROR, PREFIX_WARN
        return PREFIX_OK, PREFIX_ERROR, PREFIX_WARN
    except ImportError:
        return "OK", "[ERROR]", "[WARN]"

def detect_preferred_editor() -> str:
    """
    Detect the user's preferred text editor optimized for Linux/SSH environments.

    Priority:
    1. EDITOR environment variable
    2. VISUAL environment variable
    3. SSH-aware terminal editors
    4. Fallback to nano (universal)

    Returns:
        str: Command to launch the preferred editor
    """
    # Check environment variables first (respect user's explicit choice)
    editor = os.environ.get('EDITOR') or os.environ.get('VISUAL')
    if editor:
        return editor

    # Check if we're in SSH session (prioritize terminal editors)
    is_ssh = bool(os.environ.get('SSH_CLIENT') or os.environ.get('SSH_TTY'))

    if is_ssh:
        # SSH session: prefer lightweight terminal editors
        candidates = [
            "nano",     # User-friendly, available everywhere
            "vim",      # Powerful but requires knowledge
            "vi",       # Always available on Unix
            "emacs"     # Alternative for emacs users
        ]
    else:
        # Local session: can try GUI editors first, then terminal
        candidates = [
            "code",     # VS Code (if available)
            "nano",     # User-friendly terminal editor
            "vim",      # Vi improved
            "gedit",    # GNOME Text Editor
            "kate",     # KDE Advanced Text Editor
            "vi"        # Vi (always available)
        ]

    # Test candidates for availability
    for candidate in candidates:
        if is_command_available(candidate):
            return candidate

    # Ultimate fallback - nano is almost always available on Linux
    return "nano"

def is_command_available(command: str) -> bool:
    """
    Check if a command is available in the system PATH (Linux optimized).

    Args:
        command: Command name to check

    Returns:
        bool: True if command is available, False otherwise
    """
    try:
        # Try running the command with --version (most editors support this)
        subprocess.run(
            [command, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Fallback: use 'which' command (standard on Linux/Unix)
    try:
        result = subprocess.run(
            ["which", command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def validate_yaml_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate YAML file syntax after editing.

    Args:
        file_path: Path to the YAML file to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    # Try to get YAML validator
    yaml_validator = get_yaml_validator()
    if yaml_validator is None:
        # Fallback: basic YAML syntax check
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True, None
        except yaml.YAMLError as e:
            return False, f"YAML syntax error: {e}"
        except Exception as e:
            return False, f"File reading error: {e}"

    # Use HPone's YAML validator
    try:
        yaml_validator(file_path.stem)
        return True, None
    except Exception as e:
        return False, str(e)

def edit_honeypot_config(honeypot_name: str) -> int:
    """
    Edit a honeypot configuration file.

    Args:
        honeypot_name: Name of the honeypot to edit

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    PREFIX_OK, PREFIX_ERROR, PREFIX_WARN = get_utils()
    PROJECT_ROOT, HONEYPOT_MANIFEST_DIR = get_project_paths()

    # Construct file path
    yaml_file = HONEYPOT_MANIFEST_DIR / f"{honeypot_name}.yml"

    if not yaml_file.exists():
        print(f"{PREFIX_ERROR} Honeypot configuration not found:")
        print(f"   File: {yaml_file}")
        print(f"   Tip: Available honeypots: {', '.join([f.stem for f in HONEYPOT_MANIFEST_DIR.glob('*.yml')])}")
        return 1

    return edit_file_with_validation(yaml_file, is_yaml=True)

def edit_config_file() -> int:
    """
    Edit the main configuration file.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    PREFIX_OK, PREFIX_ERROR, PREFIX_WARN = get_utils()
    PROJECT_ROOT, _ = get_project_paths()

    config_file = PROJECT_ROOT / "hpone" / "config.py"

    if not config_file.exists():
        print(f"{PREFIX_ERROR} Configuration file not found:")
        print(f"   File: {config_file}")
        return 1

    return edit_file_with_validation(config_file, is_yaml=False)

def edit_completion_script() -> int:
    """
    Edit the bash completion script.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    PREFIX_OK, PREFIX_ERROR, PREFIX_WARN = get_utils()
    PROJECT_ROOT, _ = get_project_paths()

    completion_file = PROJECT_ROOT / "hpone" / "completion" / "hpone-completion.bash"

    if not completion_file.exists():
        print(f"{PREFIX_ERROR} Completion script not found:")
        print(f"   File: {completion_file}")
        return 1

    return edit_file_with_validation(completion_file, is_yaml=False)

def edit_file_with_validation(file_path: Path, is_yaml: bool = False) -> int:
    """
    Edit a file with the preferred editor and validate afterwards.

    Args:
        file_path: Path to the file to edit
        is_yaml: Whether to perform YAML validation after editing

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    PREFIX_OK, PREFIX_ERROR, PREFIX_WARN = get_utils()

    # Store original content for restoration if needed
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"{PREFIX_ERROR} Could not read file:")
        print(f"   Error: {e}")
        return 1

    # Get preferred editor
    editor = detect_preferred_editor()

    # Edit loop - keep editing until valid or user chooses to exit
    while True:
        print(f"{PREFIX_OK} Opening file with {editor}")
        print(f"   File: {file_path.resolve()}")

        # Launch editor
        try:
            editor_cmd = editor.split() + [str(file_path)]
            result = subprocess.run(editor_cmd, check=False)

            if result.returncode != 0:
                print(f"{PREFIX_WARN} Editor exited with code {result.returncode}")

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"{PREFIX_ERROR} Failed to launch editor '{editor}':")
            print(f"   Error: {e}")
            print(f"   Tip: Try setting EDITOR environment variable: export EDITOR=nano")
            return 1

        # Check if file was modified
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_content = f.read()

            if new_content == original_content:
                print(f"{PREFIX_OK} No changes made to {file_path.name}")
                return 0

            print(f"{PREFIX_OK} File {file_path.name} has been modified")

        except Exception as e:
            print(f"{PREFIX_ERROR} Could not read modified file:")
            print(f"   Error: {e}")
            return 1

        # Validate YAML files
        if is_yaml:
            is_valid, error_msg = validate_yaml_file(file_path)
            if not is_valid:
                print(f"{PREFIX_ERROR} YAML validation failed:")
                print(f"   Error: {error_msg}")

                # Offer options to user
                try:
                    import questionary
                    choice = questionary.select(
                        "What would you like to do?",
                        choices=[
                            "Re-edit the file",
                            "Restore original content",
                            "Keep current content (ignore validation)"
                        ]
                    ).ask()

                    if choice == "Re-edit the file":
                        # Continue the loop to edit again
                        continue
                    elif choice == "Restore original content":
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(original_content)
                        print(f"{PREFIX_OK} Original content restored")
                        return 0
                    else:  # Keep current content
                        print(f"{PREFIX_WARN} Keeping current content despite validation errors")
                        break

                except ImportError:
                    print(f"{PREFIX_WARN} Interactive prompts not available")
                    print(f"   Tip: Install questionary for better user experience: pip install questionary")
                    print(f"   {PREFIX_WARN} Keeping current content despite validation errors")
                    break
            else:
                # YAML is valid, break out of the loop
                break
        else:
            # Not a YAML file, no validation needed
            break

    print(f"{PREFIX_OK} Edit completed successfully")
    return 0

def edit_main(args) -> int:
    """
    Main entry point for the edit command.

    Args:
        args: Parsed command line arguments

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        if getattr(args, 'config', False):
            return edit_config_file()
        elif getattr(args, 'completion', False):
            return edit_completion_script()
        elif args.honeypot:
            return edit_honeypot_config(args.honeypot)
        else:
            PREFIX_OK, PREFIX_ERROR, PREFIX_WARN = get_utils()
            print(f"{PREFIX_ERROR} No target specified for edit command")
            return 1

    except KeyboardInterrupt:
        PREFIX_OK, PREFIX_ERROR, PREFIX_WARN = get_utils()
        print(f"{PREFIX_WARN} Edit cancelled by user")
        return 130
    except Exception as e:
        PREFIX_OK, PREFIX_ERROR, PREFIX_WARN = get_utils()
        print(f"{PREFIX_ERROR} Edit failed:")
        print(f"   Error: {e}")
        return 1
