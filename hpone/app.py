#!/usr/bin/env python3
"""
HPone Docker Template Manager - Modular Version

Modular application using the helpers package to manage Docker templates.
"""

from __future__ import annotations

import argparse
import sys
from typing import List

# Import semua helpers
from core import (
    # YAML operations
    load_honeypot_yaml_by_filename,
    find_honeypot_yaml_path,
    set_honeypot_enabled,
    is_honeypot_enabled,

    # Docker operations
    is_honeypot_running,
    run_compose_action,
    up_honeypot,
    down_honeypot,
    shell_honeypot,
    cleanup_global_images,
    cleanup_global_volumes,

    # Configuration handling
    parse_ports,
    parse_volumes,
    parse_env,
    normalize_host_path,
    generate_env_file,
    ensure_volume_directories,
    rewrite_compose_with_env,

    # Utility functions
    to_var_prefix,
    _format_table
)
from core.argaparse import build_arg_parser, format_full_help

from scripts import (
    # List commands
    list_honeypots,
    list_enabled_honeypot_ids,
    list_all_enabled_honeypot_ids,
    list_imported_honeypot_ids,
    resolve_honeypot_dir_id,

    # Display commands
    inspect_honeypot,

    # Import commands
    import_honeypot,

    # File operations
    ensure_destination_dir,
    find_template_dir,
    copy_template_to_destination,
    remove_honeypot,

    # Dependency checker
    require_dependencies,

    # Logs
    logs_main,

    # Clean
    clean_main,

    # Up
    up_main,

    # edit
    edit_main
)

# Import questionary for interactive prompts
try:
    import questionary
except ImportError:
    print("Error: questionary library not installed. Run: pip install questionary", file=sys.stderr)
    sys.exit(1)

from core.utils import PREFIX_OK, PREFIX_ERROR, PREFIX_WARN
from test import run_import_self_test

# Import konfigurasi ALWAYS_IMPORT
try:
    from config import ALWAYS_IMPORT
except ImportError:
    ALWAYS_IMPORT = True

def check_permissions(args):
    """Check Docker and honeypots directory permissions for commands that need them."""
    # Docker commands that require permission checks
    docker_commands = [
        "up", "down", "status", "shell", "logs", "clean", "inspect", "list"
    ]

    # Commands that need honeypots directory write access
    honeypots_write_commands = ["enable", "disable"]
    command = getattr(args, 'command', None)

    try:
        # Import locally to avoid circular imports
        from scripts.error_handlers import check_docker_permissions, check_directory_permissions

        # Check Docker permissions for Docker commands
        if command in docker_commands and not check_docker_permissions():
            return False

        # Check honeypots directory permissions for commands that modify YAML files
        if command in honeypots_write_commands:
            from pathlib import Path
            # Get honeypots directory path
            current_dir = Path(__file__).resolve().parent.parent
            honeypots_dir = current_dir / "honeypots"

            if not check_directory_permissions(str(honeypots_dir)):
                print(f"{PREFIX_ERROR} No write permission for honeypots directory: {honeypots_dir}")
                print("   Fix: Check directory permissions or run with appropriate privileges")
                print("   Or add user to docker group: sudo usermod -aG docker $USER")
                print("   Then restart your shell")
                return False

        return True

    except ImportError:
        print(f"{PREFIX_WARN} Could not import permission checkers. Continuing...", file=sys.stderr)
        return True
    except Exception as e:
        print(f"{PREFIX_WARN} Error checking permissions: {e}. Continuing...", file=sys.stderr)
        return True

def main(argv: List[str]) -> int:
    """Main entrypoint for the application."""
    parser = build_arg_parser()
    # If only -h/--help is requested, print the full help that includes all subcommands
    if any(arg in ("-h", "--help") for arg in argv):
        try:
            print(format_full_help(parser))
        except Exception:
            # Fallback to standard help if something goes wrong
            parser.print_help()
        return 0

    args = parser.parse_args(argv)

    # Run permission checks before any command execution
    if not check_permissions(args):
        return 1

    # Check dependencies command
    if args.command == "check":
        try:
            # Run import self-tests first
            if not run_import_self_test():
                return 1
            from scripts import print_dependency_status
            print_dependency_status()
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to check dependencies: {exc}", file=sys.stderr)
            return 1
        return 0

    # Check dependencies before running other commands (except 'check')
    try:
        require_dependencies()
    except SystemExit:
        return 1
    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to check dependencies: {exc}", file=sys.stderr)
        return 1

    # Import command
    if args.command == "import":
        if ALWAYS_IMPORT:
            pass; return 1

        try:
            if getattr(args, "all", False):
                # Import all enabled honeypots
                honeypot_ids = list_all_enabled_honeypot_ids()
                if not honeypot_ids:
                    print("No enabled honeypots.")
                    return 0
                print(f"Importing {len(honeypot_ids)} enabled honeypots...")
                for t in honeypot_ids:
                    try:
                        dest = import_honeypot(t, force=bool(args.force))
                        print(f"{PREFIX_OK}: Imported '{t}'")
                    except Exception as exc:
                        print(f"{PREFIX_ERROR} Failed to import '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.honeypot:
                    print("You must specify a honeypot or use --all", file=sys.stderr)
                    return 2
                dest = import_honeypot(args.honeypot, force=bool(args.force))
                print(f"{PREFIX_OK}: Imported '{args.honeypot}'")
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to import: {exc}", file=sys.stderr)
            return 1
        return 0

    # Update command
    if args.command == "update":
        if ALWAYS_IMPORT:
            pass; return 1

        try:
            honeypot_ids = list_imported_honeypot_ids()
            if not honeypot_ids:
                print("No imported honeypots.")
                return 0
            print(f"Updating {len(honeypot_ids)} imported honeypots...")
            for t in honeypot_ids:
                try:
                    dest = import_honeypot(t, force=True)
                    print(f"{PREFIX_OK}: Updated '{t}'")
                except Exception as exc:
                    print(f"{PREFIX_ERROR} Failed to update '{t}': {exc}", file=sys.stderr)
                    continue
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to update: {exc}", file=sys.stderr)
            return 1
        return 0

    # List command
    if args.command == "list":
        try:
            list_honeypots(detailed=bool(args.a))
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to list honeypots: {exc}", file=sys.stderr)
            return 1
        return 0

    # Clean command
    if args.command == "clean":
        return clean_main(args)

    # Inspect command
    if args.command == "inspect":
        try:
            inspect_honeypot(args.honeypot)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to inspect '{args.honeypot}': {exc}", file=sys.stderr)
            return 1
        return 0

    # Enable command
    if args.command == "enable":
        try:
            # Handle multiple honeypots
            for honeypot in args.honeypot:
                set_honeypot_enabled(honeypot, True)
                print(f"{PREFIX_OK}: Honeypot '{honeypot}' enabled.")
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to enable honeypots: {exc}", file=sys.stderr)
            return 1
        return 0

    # Disable command
    if args.command == "disable":
        try:
            # Handle multiple honeypots
            for honeypot in args.honeypot:
                set_honeypot_enabled(honeypot, False)
                print(f"{PREFIX_OK}: Honeypot '{honeypot}' disabled.")
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to disable honeypots: {exc}", file=sys.stderr)
            return 1
        return 0

    # Up command
    if args.command == "up":
        return up_main(args)

    # Down command
    if args.command == "down":
        try:
            if getattr(args, "all", False):
                honeypot_ids = list_imported_honeypot_ids()
                if not honeypot_ids:
                    print("No imported honeypots.")
                for t in honeypot_ids:
                    down_honeypot(t)
            else:
                if not args.honeypot:
                    print("You must specify a honeypot or use --all", file=sys.stderr)
                    return 2
                down_honeypot(args.honeypot)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to stop: {exc}", file=sys.stderr)
            return 1
        return 0

    # Shell command
    if args.command == "shell":
        try:
            shell_honeypot(args.honeypot)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to open shell in '{args.honeypot}': {exc}", file=sys.stderr)
            return 1
        return 0

    # Logs command
    if args.command == "logs":
        try:
            logs_main(args.honeypot)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to show logs for '{args.honeypot}': {exc}", file=sys.stderr)
            return 1
        return 0

    # Status command
    if args.command == "status":
        try:
            from scripts import show_status
            show_status()
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to show status: {exc}", file=sys.stderr)
            return 1
        return 0

    # Edit command
    if args.command == "edit":
        try:
            return edit_main(args)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to edit: {exc}", file=sys.stderr)
            return 1

    parser.print_help()
    return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
