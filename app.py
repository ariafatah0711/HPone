#!/usr/bin/env python3
"""
HPone Docker Template Manager - Modular Version

Aplikasi modular yang menggunakan helpers package untuk mengelola Docker templates.
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


def build_arg_parser() -> argparse.ArgumentParser:
    """Buat argument parser untuk aplikasi."""
    parser = argparse.ArgumentParser(description="HPone Docker template manager - Modular Version")
    sub = parser.add_subparsers(dest="command", required=True)

    # Import command
    p_import = sub.add_parser("import", help="Import template dan generate .env untuk tool")
    p_import.add_argument("tool", nargs="?", help="Nama tool (sesuai nama file YAML di folder tools/)")
    p_import.add_argument("--all", action="store_true", help="Import semua tool yang enabled")
    p_import.add_argument("--force", action="store_true", help="Overwrite folder docker/<tool> jika sudah ada")

    # List command
    p_list = sub.add_parser("list", help="List tools berdasarkan YAML di folder tools/")
    p_list.add_argument("-a", action="store_true", help="Tampilkan detail lengkap (deskripsi dan ports)")

    # Remove command
    p_remove = sub.add_parser("remove", help="Hapus folder docker/<tool>")
    p_remove.add_argument("tool", nargs="?", help="Nama tool yang akan dihapus")
    p_remove.add_argument("--all", action="store_true", help="Hapus semua tool yang sudah diimport")

    # Inspect command
    p_inspect = sub.add_parser("inspect", help="Tampilkan informasi detail config dari satu tool")
    p_inspect.add_argument("tool", help="Nama tool yang akan diinspect")

    # Enable command
    p_enable = sub.add_parser("enable", help="Enable tool pada tools/<tool>.yml (set enabled: true)")
    p_enable.add_argument("tool", help="Nama tool yang akan di-enable")

    # Disable command
    p_disable = sub.add_parser("disable", help="Disable tool pada tools/<tool>.yml (set enabled: false)")
    p_disable.add_argument("tool", help="Nama tool yang akan di-disable")

    # Up command
    p_up = sub.add_parser("up", help="docker compose up -d untuk satu tool atau semua tool yang enabled")
    group_up = p_up.add_mutually_exclusive_group(required=True)
    group_up.add_argument("tool", nargs="?", help="Nama tool. Jika tidak diberikan, gunakan --all")
    group_up.add_argument("--all", action="store_true", help="Jalankan untuk semua tool yang enabled dan sudah diimport")
    p_up.add_argument("--force", action="store_true", help="Force up tool meskipun tidak enabled (hanya untuk single tool)")

    # Down command
    p_down = sub.add_parser("down", help="docker compose down untuk satu tool atau semua tool yang diimport")
    group_down = p_down.add_mutually_exclusive_group(required=True)
    group_down.add_argument("tool", nargs="?", help="Nama tool. Jika tidak diberikan, gunakan --all")
    group_down.add_argument("--all", action="store_true", help="Jalankan untuk semua tool yang diimport")

    # Check dependencies command
    p_check = sub.add_parser("check", help="Check dependencies")

    return parser

def main(argv: List[str]) -> int:
    """Main function untuk aplikasi."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Check dependencies command
    if args.command == "check":
        try:
            from scripts import print_dependency_status
            print_dependency_status()
        except Exception as exc:
            print(f"[ERROR] Gagal check dependencies: {exc}", file=sys.stderr)
            return 1
        return 0

    # Check dependencies sebelum menjalankan command lain (kecuali check)
    try:
        require_dependencies()
    except SystemExit:
        return 1
    except Exception as exc:
        print(f"[ERROR] Gagal check dependencies: {exc}", file=sys.stderr)
        return 1

    # Import command
    if args.command == "import":
        try:
            if getattr(args, "all", False):
                # Import semua tool yang enabled
                tool_ids = list_all_enabled_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool yang enabled.")
                    return 0
                print(f"Importing {len(tool_ids)} enabled tools...")
                for t in tool_ids:
                    try:
                        dest = import_tool(t, force=bool(args.force))
                        print(f"OK: Template '{t}' diimport ke: {dest}")
                    except Exception as exc:
                        print(f"[ERROR] Gagal import '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                dest = import_tool(args.tool, force=bool(args.force))
                print(f"OK: Template '{args.tool}' diimport ke: {dest}")
                print(f"OK: File .env dibuat di: {dest / '.env'}")
        except Exception as exc:
            print(f"[ERROR] Gagal import: {exc}", file=sys.stderr)
            return 1
        return 0

    # List command
    if args.command == "list":
        try:
            list_tools(detailed=bool(args.a))
        except Exception as exc:
            print(f"[ERROR] Gagal list tools: {exc}", file=sys.stderr)
            return 1
        return 0

    # Remove command
    if args.command == "remove":
        try:
            if getattr(args, "all", False):
                # Remove semua tool yang sudah diimport
                tool_ids = list_imported_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool yang diimport.")
                    return 0
                print(f"Removing {len(tool_ids)} imported tools...")
                for t in tool_ids:
                    try:
                        remove_tool(t)
                    except Exception as exc:
                        print(f"[ERROR] Gagal remove '{t}': {exc}", file=sys.stderr)
                        continue
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                remove_tool(args.tool)
        except Exception as exc:
            print(f"[ERROR] Gagal remove: {exc}", file=sys.stderr)
            return 1
        return 0

    # Inspect command
    if args.command == "inspect":
        try:
            inspect_tool(args.tool)
        except Exception as exc:
            print(f"[ERROR] Gagal inspect '{args.tool}': {exc}", file=sys.stderr)
            return 1
        return 0

    # Enable command
    if args.command == "enable":
        try:
            set_tool_enabled(args.tool, True)
        except Exception as exc:
            print(f"[ERROR] Gagal enable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"OK: Tool '{args.tool}' enabled.")
        return 0

    # Disable command
    if args.command == "disable":
        try:
            set_tool_enabled(args.tool, False)
        except Exception as exc:
            print(f"[ERROR] Gagal disable '{args.tool}': {exc}", file=sys.stderr)
            return 1
        print(f"OK: Tool '{args.tool}' disabled.")
        return 0

    # Up command
    if args.command == "up":
        try:
            if getattr(args, "all", False):
                # For --all, ignore force flag and only up enabled tools
                tool_ids = list_enabled_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool enabled yang sudah diimport.")
                for t in tool_ids:
                    up_tool(t, force=False)
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                up_tool(args.tool, force=bool(args.force))
        except Exception as exc:
            print(f"[ERROR] Gagal up: {exc}", file=sys.stderr)
            return 1
        return 0

    # Down command
    if args.command == "down":
        try:
            if getattr(args, "all", False):
                tool_ids = list_imported_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool yang diimport.")
                for t in tool_ids:
                    down_tool(t)
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                down_tool(args.tool)
        except Exception as exc:
            print(f"[ERROR] Gagal down: {exc}", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
