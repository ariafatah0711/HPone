"""
Display helpers for HPone.

Functions to render clean and informative output.
"""

import glob
from pathlib import Path
from typing import List

try:
    import yaml  # type: ignore
except ImportError:
    raise ImportError("PyYAML diperlukan untuk modul ini")

# Import constants dan functions dari helpers
from core.constants import TOOLS_DIR, OUTPUT_DOCKER_DIR
from core.utils import _format_table, PREFIX_ERROR
from core.config import parse_ports, parse_volumes
from core.docker import is_tool_running

# Fungsi list_tools dipindah ke scripts/list.py untuk avoid duplication

def inspect_tool(tool_id: str) -> None:
    """Show detailed information about a tool."""
    try:
        from core.yaml import load_tool_yaml_by_filename, find_tool_yaml_path
        resolved_name, config = load_tool_yaml_by_filename(tool_id)
    except FileNotFoundError as exc:
        print(f"{PREFIX_ERROR} Tool '{tool_id}' not found: {exc}")
        return
    except Exception as exc:
        print(f"{PREFIX_ERROR} Failed to load config for tool '{tool_id}': {exc}")
        return

    # Status info
    enabled_flag = bool(config.get("enabled") is True)
    imported_flag = (OUTPUT_DOCKER_DIR / tool_id).exists()
    running_flag = is_tool_running(tool_id)

    # Status indicators
    enabled_icon = "✅" if enabled_flag else "❌"
    imported_icon = "📦" if imported_flag else "📭"
    status_icon = "🟢" if running_flag else "🔴"

    enabled_str = "Enabled" if enabled_flag else "Disabled"
    imported_str = "Imported" if imported_flag else "Not Imported"
    status_str = "Running" if running_flag else "Stopped"

    # Simple header like check command
    print(f"🔍 Inspecting tool '{resolved_name}'...")
    print()

    # Basic info
    print("📋 Basic Information:")
    print(f"   {status_icon} Status: {status_str}")
    print(f"   {enabled_icon} {enabled_str}")
    print(f"   {imported_icon} {imported_str}")

    # Description if available
    desc = config.get("description")
    if desc:
        print(f"   📝 {desc}")
    print()

    # Ports section
    try:
        ports = parse_ports(config)
        if ports:
            print(f"🔌 Ports ({len(ports)} configured):")
            for host, container in ports:
                print(f"   {host:>6} → {container:<6}")
        else:
            print("🔌 Ports: None configured")
    except Exception as exc:
        print(f"🔌 Ports: Error parsing ({exc})")
    print()

    # Volumes section
    try:
        volumes = parse_volumes(config)
        if volumes:
            print(f"💾 Volumes ({len(volumes)} configured):")
            for src, dst in volumes:
                print(f"   {src} → {dst}")
        else:
            print("💾 Volumes: None configured")
    except Exception as exc:
        print(f"💾 Volumes: Error parsing ({exc})")
    print()

    # Environment variables
    env_vars = config.get("env") or {}
    if env_vars:
        print(f"🔧 Environment Variables ({len(env_vars)} configured):")
        for key, value in env_vars.items():
            print(f"   {key} = {value}")
    else:
        print("🔧 Environment Variables: None configured")
    print()

    # Service selection
    service = config.get("service")
    services = config.get("services")
    if service or services:
        print("⚙️  Service Selection:")
        if service:
            print(f"   Service: {service}")
        if services:
            print(f"   Services: {', '.join(map(str, services))}")
        print()

    # File paths
    try:
        yaml_path = find_tool_yaml_path(tool_id)
        print("📁 File Information:")
        print(f"   Config: {yaml_path}")

        if imported_flag:
            docker_dir = OUTPUT_DOCKER_DIR / tool_id
            print(f"   Docker: {docker_dir}")

            env_file = docker_dir / ".env"
            if env_file.exists():
                print(f"   .env: {env_file}")
        else:
            print("   Docker: Not imported")
    except Exception as exc:
        print(f"📁 File Information: Error ({exc})")

    print(f"\n🎉 Inspection complete!")
