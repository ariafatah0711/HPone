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
    require_dependencies
)

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
            from scripts import print_dependency_status
            print_dependency_status()
        except Exception as exc:
            print(f"[ERROR] Failed to check dependencies: {exc}", file=sys.stderr)
            return 1
        return 0

    # Check dependencies before running other commands (except 'check')
    try:
        require_dependencies()
    except SystemExit:
        return 1
    except Exception as exc:
        print(f"[ERROR] Failed to check dependencies: {exc}", file=sys.stderr)
        return 1

    # Import command
    if args.command == "import":
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
                        print(f"OK: Template '{t}' imported to: {dest}")
                    except Exception as exc:
                        print(f"[ERROR] Failed to import '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("You must specify a tool or use --all", file=sys.stderr)
                    return 2
                dest = import_tool(args.tool, force=bool(args.force))
                print(f"OK: Template '{args.tool}' imported to: {dest}")
                print(f"OK: .env file created at: {dest / '.env'}")
        except Exception as exc:
            print(f"[ERROR] Failed to import: {exc}", file=sys.stderr)
            return 1
        return 0

    # Update command
    if args.command == "update":
        try:
            tool_ids = list_imported_tool_ids()
            if not tool_ids:
                print("No imported tools.")
                return 0
            print(f"Updating {len(tool_ids)} imported tools...")
            for t in tool_ids:
                try:
                    dest = import_tool(t, force=True)
                    print(f"OK: Template '{t}' updated at: {dest}")
                except Exception as exc:
                    print(f"[ERROR] Failed to update '{t}': {exc}", file=sys.stderr)
                    continue
        except Exception as exc:
            print(f"[ERROR] Failed to update: {exc}", file=sys.stderr)
            return 1
        return 0

    # List command
    if args.command == "list":
        try:
            list_tools(detailed=bool(args.a))
        except Exception as exc:
            print(f"[ERROR] Failed to list tools: {exc}", file=sys.stderr)
            return 1
        return 0

    # Remove command
    if args.command == "remove":
        try:
            if getattr(args, "all", False):
                # Remove all imported tools
                tool_ids = list_imported_tool_ids()
                if not tool_ids:
                    print("No imported tools.")
                    return 0
                print(f"Removing {len(tool_ids)} imported tools...")
                for t in tool_ids:
                    try:
                        remove_tool(t)
                    except Exception as exc:
                        print(f"[ERROR] Failed to remove '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("You must specify a tool or use --all", file=sys.stderr)
                    return 2
                remove_tool(args.tool)
        except Exception as exc:
            print(f"[ERROR] Failed to remove: {exc}", file=sys.stderr)
            return 1
        return 0

    # Inspect command
    if args.command == "inspect":
        try:
            inspect_tool(args.tool)
        except Exception as exc:
            print(f"[ERROR] Failed to inspect '{args.tool}': {exc}", file=sys.stderr)
            return 1
        return 0

    # Enable command
    if args.command == "enable":
        try:
            set_tool_enabled(args.tool, True)
        except Exception as exc:
            print(f"[ERROR] Failed to enable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"OK: Tool '{args.tool}' enabled.")
        return 0

    # Disable command
    if args.command == "disable":
        try:
            set_tool_enabled(args.tool, False)
        except Exception as exc:
            print(f"[ERROR] Failed to disable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"OK: Tool '{args.tool}' disabled.")
        return 0

    # Up command
    if args.command == "up":
        try:
            if getattr(args, "all", False):
                # For --all, ignore force flag and only up enabled tools
                # If --update, update all imported tools first
                if getattr(args, "update", False):
                    imported_ids = list_imported_tool_ids()
                    if imported_ids:
                        print(f"Updating {len(imported_ids)} imported tools before up...")
                        for t in imported_ids:
                            try:
                                dest = import_tool(t, force=True)
                                print(f"OK: Template '{t}' updated at: {dest}")
                            except Exception as exc:
                                print(f"[WARN] Failed to update '{t}': {exc}")
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
                # If --update for a single tool, update first only if already imported
                if getattr(args, "update", False):
                    try:
                        from core.constants import OUTPUT_DOCKER_DIR
                        if (OUTPUT_DOCKER_DIR / args.tool).exists():
                            dest = import_tool(args.tool, force=True)
                            print(f"OK: Template '{args.tool}' updated at: {dest}")
                        else:
                            print(f"Skip update: tool '{args.tool}' is not imported.")
                    except Exception as exc:
                        print(f"[ERROR] Failed to update '{args.tool}': {exc}", file=sys.stderr)
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
                        print(f"[ERROR] Tool '{args.tool}' not found in '{TOOLS_DIR}'.", file=sys.stderr)
                        return 1

                    reply = input(f"Tool '{args.tool}' is not imported. Import now? [y/N]: ").strip().lower()
                    if reply in ("y", "yes", "ya"):
                        try:
                            dest = import_tool(args.tool, force=False)
                            print(f"OK: Template '{args.tool}' imported to: {dest}")
                            print(f"OK: .env file created at: {dest / '.env'}")
                            up_tool(args.tool, force=bool(args.force))
                        except Exception as exc:
                            print(f"[ERROR] Failed to start '{args.tool}': {exc}", file=sys.stderr)
                            return 1
                    else:
                        print("Cancelled.")
                        return 0
        except Exception as exc:
            print(f"[ERROR] Failed to start: {exc}", file=sys.stderr)
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
            print(f"[ERROR] Failed to stop: {exc}", file=sys.stderr)
            return 1
        return 0

    # Status command (running only)
    if args.command == "status":
        try:
            # Get all imported tools
            tool_ids = list_imported_tool_ids()
            if not tool_ids:
                print("No imported tools.")
                return 0

            # Filter only running ones
            running_tools = []
            for t in tool_ids:
                try:
                    if is_tool_running(t):
                        running_tools.append(t)
                except Exception:
                    continue

            if not running_tools:
                print("No tools are running.")
                return 0

            # Collect port mappings
            rows = []
            for t in running_tools:
                try:
                    # Read tool YAML for port mapping
                    _resolved_name, cfg = load_tool_yaml_by_filename(t)
                    from core.config import parse_ports
                    port_pairs = parse_ports(cfg)
                except Exception:
                    port_pairs = []

                # Add row per mapping host->container
                for host, container in port_pairs:
                    # Normalize container column to only main number before "/udp" if any
                    rows.append([str(host), str(container), t])

            # Sort by HOST numerically if possible
            def _key_host(row):
                try:
                    return int(str(row[0]).split("/")[0])
                except Exception:
                    return str(row[0])

            rows.sort(key=_key_host)

            # Render table
            from core.utils import _format_table
            table = _format_table(["HOST", "CONTAINER", "SERVICE"], rows, max_width=30)
            if table:
                print(table)
            print(f"\n{len(running_tools)} tools running")
        except Exception as exc:
            print(f"[ERROR] Failed to show status: {exc}", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))