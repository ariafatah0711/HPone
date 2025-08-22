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
    load_tool_yaml_by_filename,
    find_tool_yaml_path,
    set_tool_enabled,
    is_tool_enabled,

    # Docker operations
    is_tool_running,
    run_compose_action,
    up_tool,
    down_tool,
    shell_tool,

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
    list_tools,
    list_enabled_tool_ids,
    list_all_enabled_tool_ids,
    list_imported_tool_ids,
    resolve_tool_dir_id,

    # Display commands
    inspect_tool,

    # Import commands
    import_tool,

    # File operations
    ensure_destination_dir,
    find_template_dir,
    copy_template_to_destination,
    remove_tool,

    # Dependency checker
    require_dependencies,

    # Logs
    logs_main
)

from core.utils import PREFIX_OK, PREFIX_ERROR, PREFIX_WARN
from test import run_import_self_test

# Import konfigurasi ALWAYS_IMPORT
try:
    from config import ALWAYS_IMPORT
except ImportError:
    ALWAYS_IMPORT = True

## Self-test moved to test.run_import_self_test

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
                # Import all enabled tools
                tool_ids = list_all_enabled_tool_ids()
                if not tool_ids:
                    print("No enabled tools.")
                    return 0
                print(f"Importing {len(tool_ids)} enabled tools...")
                for t in tool_ids:
                    try:
                        dest = import_tool(t, force=bool(args.force))
                        print(f"{PREFIX_OK}: Imported '{t}'")
                    except Exception as exc:
                        print(f"{PREFIX_ERROR} Failed to import '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("You must specify a tool or use --all", file=sys.stderr)
                    return 2
                dest = import_tool(args.tool, force=bool(args.force))
                print(f"{PREFIX_OK}: Imported '{args.tool}'")
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to import: {exc}", file=sys.stderr)
            return 1
        return 0

    # Update command
    if args.command == "update":
        if ALWAYS_IMPORT:
            pass; return 1

        try:
            tool_ids = list_imported_tool_ids()
            if not tool_ids:
                print("No imported tools.")
                return 0
            print(f"Updating {len(tool_ids)} imported tools...")
            for t in tool_ids:
                try:
                    dest = import_tool(t, force=True)
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
            list_tools(detailed=bool(args.a))
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to list tools: {exc}", file=sys.stderr)
            return 1
        return 0

    # Clean command
    if args.command == "clean":
        try:
            if getattr(args, "all", False):
                # Clean all imported tools; if none but --data specified, still remove data directories
                imported_ids = list_imported_tool_ids()
                # Optional data removal confirmation for --all
                remove_data_all = False
                if getattr(args, "data", False):
                    reply = input("This will remove mounted data under data/<tool> for ALL tools. Continue? [y/N]: ").strip().lower()
                    print()  # Add newline after input
                    remove_data_all = reply in ("y", "yes", "ya")

                if not imported_ids:
                    if remove_data_all:
                        try:
                            # Remove all data directories under DATA_DIR even if nothing is imported
                            from core.constants import DATA_DIR
                            from scripts import remove_tool_data
                            # Iterate over immediate subdirectories in DATA_DIR
                            if DATA_DIR.exists():
                                print("No imported tools. Removing data directories under data/...")
                                for d in sorted([p for p in DATA_DIR.iterdir() if p.is_dir()]):
                                    try:
                                        remove_tool_data(d.name)
                                    except Exception as exc_data:
                                        print(f"{PREFIX_WARN} Failed to remove data for '{d.name}': {exc_data}")
                            else:
                                print("No data directory found.")
                        except Exception as exc:
                            print(f"{PREFIX_ERROR} Failed to remove data: {exc}", file=sys.stderr)
                            return 1
                        return 0
                    else:
                        print("No imported tools.")
                        return 0

                print(f"Cleaning {len(imported_ids)} imported tools (down + remove{' + data' if remove_data_all else ''}{' + images' if getattr(args, 'image', False) else ''}{' + volumes' if getattr(args, 'volume', False) else ''})...")
                for t in imported_ids:
                    try:
                        # Down first
                        down_tool(
                            t,
                            remove_volumes=bool(getattr(args, "volume", False)),
                            remove_images=bool(getattr(args, "image", False)),
                        )

                        # Remove data if confirmed
                        if remove_data_all:
                            try:
                                from scripts import remove_tool_data
                                remove_tool_data(t)  # This prints its own success message
                            except Exception as exc_data:
                                print(f"{PREFIX_WARN} Failed to remove data for '{t}': {exc_data}")

                        # Show image/volume removal status (docker compose down with flags doesn't show explicit confirmation)
                        if getattr(args, "image", False):
                            print(f"{PREFIX_OK}: Removed images for {t}")

                        if getattr(args, "volume", False):
                            print(f"{PREFIX_OK}: Removed volumes for {t}")

                        # Then remove docker directory
                        remove_tool(t)  # This prints its own success message
                    except Exception as exc:
                        print(f"{PREFIX_ERROR} Failed to clean '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("You must specify a tool or use --all", file=sys.stderr)
                    return 2
                # Down first
                down_tool(
                    args.tool,
                    remove_volumes=bool(getattr(args, "volume", False)),
                    remove_images=bool(getattr(args, "image", False)),
                )

                # Optionally remove data for single tool
                if getattr(args, "data", False):
                    try:
                        from scripts import remove_tool_data
                        remove_tool_data(args.tool)  # This prints its own success message
                    except Exception as exc_data:
                        print(f"{PREFIX_WARN} Failed to remove data for '{args.tool}': {exc_data}")

                # Show image/volume removal status (docker compose down with flags doesn't show explicit confirmation)
                if getattr(args, "image", False):
                    print(f"{PREFIX_OK}: Removed images for {args.tool}")

                if getattr(args, "volume", False):
                    print(f"{PREFIX_OK}: Removed volumes for {args.tool}")

                # Then remove docker directory
                remove_tool(args.tool)  # This prints its own success message
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to clean: {exc}", file=sys.stderr)
            return 1
        return 0

    # Inspect command
    if args.command == "inspect":
        try:
            inspect_tool(args.tool)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to inspect '{args.tool}': {exc}", file=sys.stderr)
            return 1
        return 0

    # Enable command
    if args.command == "enable":
        try:
            set_tool_enabled(args.tool, True)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to enable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"{PREFIX_OK}: Tool '{args.tool}' enabled.")
        return 0

    # Disable command
    if args.command == "disable":
        try:
            set_tool_enabled(args.tool, False)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to disable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"{PREFIX_OK}: Tool '{args.tool}' disabled.")
        return 0

    # Up command
    if args.command == "up":
        try:
            if getattr(args, "all", False):
                # For --all, handle ALWAYS_IMPORT differently
                if ALWAYS_IMPORT:
                    # Auto-import all enabled tools first
                    tool_ids = list_all_enabled_tool_ids()
                    if not tool_ids:
                        print("No enabled tools.")
                        return 0

                    print(f"Auto-importing {len(tool_ids)} enabled tools...")
                    for t in tool_ids:
                        try:
                            dest = import_tool(t, force=True)
                            # print(f"{PREFIX_OK}: Auto-imported '{t}'")
                        except Exception as exc:
                            print(f"{PREFIX_ERROR} Failed to auto-import '{t}': {exc}", file=sys.stderr)
                            continue

                    print(f"Starting {len(tool_ids)} tools...")
                    for t in tool_ids:
                        try:
                            up_tool(t, force=False)
                        except Exception as exc:
                            print(f"{PREFIX_ERROR} Failed to start '{t}': {exc}", file=sys.stderr)
                            continue
                else:
                    # Original logic for ALWAYS_IMPORT=false
                    # If --update, update all imported tools first
                    if getattr(args, "update", False):
                        imported_ids = list_imported_tool_ids()
                        if imported_ids:
                            print(f"Updating {len(imported_ids)} imported tools before up...")
                            for t in imported_ids:
                                try:
                                    dest = import_tool(t, force=True)
                                    print(f"{PREFIX_OK}: Template '{t}' updated at: {dest}")
                                except Exception as exc:
                                    print(f"{PREFIX_WARN} Failed to update '{t}': {exc}")
                        else:
                            print("No imported tools to update.")

                    tool_ids = list_enabled_tool_ids()
                    if not tool_ids:
                        print("No enabled and imported tools.")
                    for t in tool_ids:
                        up_tool(t, force=False)
            else:
                if not args.tool:
                    print("You must specify a tool or use --all", file=sys.stderr)
                    return 2

                # Auto-import if ALWAYS_IMPORT=true
                if ALWAYS_IMPORT:
                    try:
                        # First check if tool exists
                        from core.constants import TOOLS_DIR
                        from core.yaml import find_tool_yaml_path
                        try:
                            find_tool_yaml_path(args.tool)
                        except FileNotFoundError:
                            print(f"{PREFIX_ERROR} Tool '{args.tool}' not found in '{TOOLS_DIR}'.", file=sys.stderr)
                            return 1

                        # Then check if tool is enabled
                        if not is_tool_enabled(args.tool):
                            if not getattr(args, "force", False):
                                print(f"{PREFIX_ERROR} Tool '{args.tool}' is not enabled. Use --force to override.", file=sys.stderr)
                                return 1
                            print(f"{PREFIX_WARN} Tool '{args.tool}' is not enabled, but continuing with --force")

                        # Auto-import the tool
                        dest = import_tool(args.tool, force=True)
                        # print(f"{PREFIX_OK}: Auto-imported '{args.tool}'")

                        # Start the tool
                        up_tool(args.tool, force=bool(args.force))
                        return 0

                    except Exception as exc:
                        print(f"{PREFIX_ERROR} Failed to auto-import and start '{args.tool}': {exc}", file=sys.stderr)
                        return 1

                # Original logic for ALWAYS_IMPORT=false
                # If --update for a single tool, update first only if already imported
                if getattr(args, "update", False):
                    try:
                        from core.constants import OUTPUT_DOCKER_DIR
                        if (OUTPUT_DOCKER_DIR / args.tool).exists():
                            dest = import_tool(args.tool, force=True)
                            print(f"{PREFIX_OK}: Updated '{args.tool}'")
                        else:
                            print(f"Skip update: tool '{args.tool}' is not imported.")
                    except Exception as exc:
                        print(f"{PREFIX_ERROR} Failed to update '{args.tool}': {exc}", file=sys.stderr)
                        return 1
                try:
                    up_tool(args.tool, force=bool(args.force))
                except FileNotFoundError:
                    # Verify the tool exists in tools/ before offering import
                    try:
                        from core.constants import TOOLS_DIR
                        from core.yaml import find_tool_yaml_path
                        find_tool_yaml_path(args.tool)
                    except FileNotFoundError:
                        print(f"{PREFIX_ERROR} Tool '{args.tool}' not found in '{TOOLS_DIR}'.", file=sys.stderr)
                        return 1

                    reply = input(f"Tool '{args.tool}' is not imported. Import now? [y/N]: ").strip().lower()
                    if reply in ("y", "yes", "ya"):
                        try:
                            dest = import_tool(args.tool, force=False)
                            print(f"{PREFIX_OK}: Imported '{args.tool}'")
                            up_tool(args.tool, force=bool(args.force))
                        except Exception as exc:
                            print(f"{PREFIX_ERROR} Failed to start '{args.tool}': {exc}", file=sys.stderr)
                            return 1
                    else:
                        print("Cancelled.")
                        return 0
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to start: {exc}", file=sys.stderr)
            return 1
        return 0

    # Down command
    if args.command == "down":
        try:
            if getattr(args, "all", False):
                tool_ids = list_imported_tool_ids()
                if not tool_ids:
                    print("No imported tools.")
                for t in tool_ids:
                    down_tool(t)
            else:
                if not args.tool:
                    print("You must specify a tool or use --all", file=sys.stderr)
                    return 2
                down_tool(args.tool)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to stop: {exc}", file=sys.stderr)
            return 1
        return 0

    # Shell command
    if args.command == "shell":
        try:
            shell_tool(args.tool)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to open shell in '{args.tool}': {exc}", file=sys.stderr)
            return 1
        return 0

    # Logs command
    if args.command == "logs":
        try:
            logs_main(args.tool)
        except Exception as exc:
            print(f"{PREFIX_ERROR} Failed to show logs for '{args.tool}': {exc}", file=sys.stderr)
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

    parser.print_help()
    return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
