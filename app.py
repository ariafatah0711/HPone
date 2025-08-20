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
    """Main function untuk aplikasi."""
    parser = build_arg_parser()
    # Jika hanya diminta -h/--help, tampilkan full help yang mencakup semua subcommands
    if any(arg in ("-h", "--help") for arg in argv):
        try:
            print(format_full_help(parser))
        except Exception:
            # fallback ke help standar jika terjadi error
            parser.print_help()
        return 0

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

    # Update command
    if args.command == "update":
        try:
            tool_ids = list_imported_tool_ids()
            if not tool_ids:
                print("Tidak ada tool yang diimport.")
                return 0
            print(f"Updating {len(tool_ids)} imported tools...")
            for t in tool_ids:
                try:
                    dest = import_tool(t, force=True)
                    print(f"OK: Template '{t}' diupdate di: {dest}")
                except Exception as exc:
                    print(f"[ERROR] Gagal update '{t}': {exc}", file=sys.stderr)
                    continue
        except Exception as exc:
            print(f"[ERROR] Gagal update: {exc}", file=sys.stderr)
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
                # Jika --update, update semua yang sudah diimport terlebih dahulu
                if getattr(args, "update", False):
                    imported_ids = list_imported_tool_ids()
                    if imported_ids:
                        print(f"Updating {len(imported_ids)} imported tools before up...")
                        for t in imported_ids:
                            try:
                                dest = import_tool(t, force=True)
                                print(f"OK: Template '{t}' diupdate di: {dest}")
                            except Exception as exc:
                                print(f"[WARN] Gagal update '{t}': {exc}")
                    else:
                        print("Tidak ada tool yang diimport untuk diupdate.")

                tool_ids = list_enabled_tool_ids()
                if not tool_ids:
                    print("Tidak ada tool enabled yang sudah diimport.")
                for t in tool_ids:
                    up_tool(t, force=False)
            else:
                if not args.tool:
                    print("Harus beri nama tool atau gunakan --all", file=sys.stderr)
                    return 2
                # Jika --update untuk single tool, lakukan update dulu hanya jika sudah diimport
                if getattr(args, "update", False):
                    try:
                        from core.constants import OUTPUT_DOCKER_DIR
                        if (OUTPUT_DOCKER_DIR / args.tool).exists():
                            dest = import_tool(args.tool, force=True)
                            print(f"OK: Template '{args.tool}' diupdate di: {dest}")
                        else:
                            print(f"Lewati update: tool '{args.tool}' belum diimport.")
                    except Exception as exc:
                        print(f"[ERROR] Gagal update '{args.tool}': {exc}", file=sys.stderr)
                        return 1
                try:
                    up_tool(args.tool, force=bool(args.force))
                except FileNotFoundError:
                    reply = input(f"Tool '{args.tool}' belum diimport. Import sekarang? [y/N]: ").strip().lower()
                    if reply in ("y", "ya", "yes"):
                        try:
                            dest = import_tool(args.tool, force=False)
                            print(f"OK: Template '{args.tool}' diimport ke: {dest}")
                            print(f"OK: File .env dibuat di: {dest / '.env'}")
                            up_tool(args.tool, force=bool(args.force))
                        except Exception as exc:
                            print(f"[ERROR] Gagal Up '{args.tool}': {exc}", file=sys.stderr)
                            return 1
                    else:
                        print("Dibatalkan.")
                        return 0
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

    # Status command (running only)
    if args.command == "status":
        try:
            # Ambil semua tool yang sudah diimport
            tool_ids = list_imported_tool_ids()
            if not tool_ids:
                print("Tidak ada tool yang diimport.")
                return 0

            # Filter yang running saja
            running_tools = []
            for t in tool_ids:
                try:
                    if is_tool_running(t):
                        running_tools.append(t)
                except Exception:
                    continue

            if not running_tools:
                print("Tidak ada tool yang sedang running.")
                return 0

            # Kumpulkan port mappings
            rows = []
            for t in running_tools:
                try:
                    # Baca YAML tool untuk port mapping
                    _resolved_name, cfg = load_tool_yaml_by_filename(t)
                    from core.config import parse_ports
                    port_pairs = parse_ports(cfg)
                except Exception:
                    port_pairs = []

                # Tambahkan baris per mapping host->container
                for host, container in port_pairs:
                    # Normalisasi agar hanya angka utama sebelum "/udp" jika ada untuk kolom container
                    rows.append([str(host), str(container), t])

            # Urutkan berdasarkan HOST numerik jika bisa
            def _key_host(row):
                try:
                    return int(str(row[0]).split("/")[0])
                except Exception:
                    return str(row[0])

            rows.sort(key=_key_host)

            # Render tabel
            from core.utils import _format_table
            table = _format_table(["HOST", "CONTAINER", "SERVICE"], rows, max_width=30)
            if table:
                print(table)
            print(f"\n{len(running_tools)} tools running")
        except Exception as exc:
            print(f"[ERROR] Gagal menampilkan status: {exc}", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 2

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))