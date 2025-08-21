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

    # Status indicators with emoji for better visuals
    enabled_icon = "✅" if enabled_flag else "❌"
    imported_icon = "📦" if imported_flag else "📭"
    status_icon = "🟢" if running_flag else "🔴"
    
    enabled_str = "Enabled" if enabled_flag else "Disabled"
    imported_str = "Imported" if imported_flag else "Not Imported"
    status_str = "Running" if running_flag else "Stopped"

    # Nicer header
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print(f"║                           🔍 INSPECT TOOL: {resolved_name:<33} ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    
    # Basic info dengan format yang rapi
    print(f"\n📋 BASIC INFORMATION")
    print("   ┌─────────────────────────────────────────────────────────────────────────┐")
    print(f"   │ Name        : {resolved_name:<57} │")
    # Wrap description into two lines with ':' alignment
    try:
        import textwrap
        desc = str(config.get("description", "No description"))
        content_width = 57
        wrapped_desc = textwrap.wrap(desc, width=content_width) or [""]
        if len(wrapped_desc) < 2:
            wrapped_desc += [""]
        wrapped_desc = wrapped_desc[:2]
        desc_label = "Description"
        first_prefix = "   │ " + f"{desc_label} : "
        second_prefix = "   │ " + " " * (len(desc_label) + 1) + ": "
        print(f"{first_prefix}{wrapped_desc[0]:<{content_width}} │")
        print(f"{second_prefix}{wrapped_desc[1]:<{content_width}} │")
    except Exception:
        print(f"   │ Description : {str(config.get('description', 'No description')):<57} │")
    print(f"   │ Status      : {status_icon} {status_str:<54} │")
    print(f"   │ Enabled     : {enabled_icon} {enabled_str:<54} │")
    print(f"   │ Imported    : {imported_icon} {imported_str:<54} │")
    print("   └─────────────────────────────────────────────────────────────────────────┘")
    
    # Ports section
    try:
        ports = parse_ports(config)
        if ports:
            print(f"\n🔌 PORTS ({len(ports)} configured)")
            print("   ┌─────────────────────────────────────────────────────────────────────────┐")
            for i, (host, container) in enumerate(ports, 1):
                print(f"   │ Port {i:2d} : {host:>6} → {container:<6} {'':<45} │")
            print("   └─────────────────────────────────────────────────────────────────────────┘")
        else:
            print(f"\n🔌 PORTS")
            print("   ┌─────────────────────────────────────────────────────────────────────────┐")
            print("   │ No ports configured                                                     │")
            print("   └─────────────────────────────────────────────────────────────────────────┘")
    except Exception as exc:
        print(f"\n🔌 PORTS")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        error_str = str(exc)
        if len(error_str) > 50:
            error_str = error_str[:47] + "..."
        print(f"   │ Error parsing ports: {error_str:<55} │")
        print("   └─────────────────────────────────────────────────────────────────────────┘")

    # Volumes section
    try:
        volumes = parse_volumes(config)
        if volumes:
            print(f"\n💾 VOLUMES ({len(volumes)} configured)")
            print("   ┌─────────────────────────────────────────────────────────────────────────┐")
            for i, (src, dst) in enumerate(volumes, 1):
                from core.config import normalize_host_path
                normalized_src = normalize_host_path(src)
                # Truncate src dan dst jika terlalu panjang
                src_display = src if len(src) <= 25 else "..." + src[-22:]
                dst_display = dst if len(dst) <= 20 else "..." + dst[-17:]
                print(f"   │ Volume {i:2d}: {src_display:<28} → {dst_display:<29} │")

                # Truncate normalized path jika terlalu panjang
                norm_display = str(normalized_src)
                if len(norm_display) > 50:
                    norm_display = "..." + norm_display[-47:]
                print(f"   │            normalized: {norm_display:<48} │")
            print("   └─────────────────────────────────────────────────────────────────────────┘")
        else:
            print(f"\n💾 VOLUMES")
            print("   ┌─────────────────────────────────────────────────────────────────────────┐")
            print("   │ No volumes configured                                                   │")
            print("   └─────────────────────────────────────────────────────────────────────────┘")
    except Exception as exc:
        print(f"\n💾 VOLUMES")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        error_str = str(exc)
        if len(error_str) > 50:
            error_str = error_str[:47] + "..."
        print(f"   │ Error parsing volumes: {error_str:<50} │")
        print("   └─────────────────────────────────────────────────────────────────────────┘")

    # Environment variables
    env_vars = config.get("env") or {}
    if env_vars:
        print(f"\n🔧 ENVIRONMENT VARIABLES ({len(env_vars)} configured)")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        for key, value in env_vars.items():
            key_display = str(key) if len(str(key)) <= 20 else "..." + str(key)[-17:]
            value_display = str(value) if len(str(value)) <= 40 else "..." + str(value)[-37:]
            print(f"   │ {key_display:<20} : {value_display:<41} │")
        print("   └─────────────────────────────────────────────────────────────────────────┘")
    else:
        print(f"\n🔧 ENVIRONMENT VARIABLES")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        print("   │ No environment variables configured                                     │")
        print("   └─────────────────────────────────────────────────────────────────────────┘")

    # Service selection (if present)
    service = config.get("service")
    services = config.get("services")
    if service or services:
        print(f"\n⚙️  SERVICE SELECTION")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        if service:
            service_display = str(service) if len(str(service)) <= 60 else "..." + str(service)[-57:]
            print(f"   │ Service  : {service_display:<60} │")
        if services:
            services_str = ', '.join(map(str, services))
            services_display = services_str if len(services_str) <= 60 else "..." + services_str[-57:]
            print(f"   │ Services : {services_display:<60} │")
        print("   └─────────────────────────────────────────────────────────────────────────┘")

    # File path info
    try:
        yaml_path = find_tool_yaml_path(tool_id)
        print(f"\n📁 FILE INFORMATION")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        
        # Config file
        config_file_str = str(yaml_path)
        if len(config_file_str) > 50:
            config_file_str = "..." + config_file_str[-47:]
        print(f"   │ Config file     : {config_file_str:<53} │")
        
        if imported_flag:
            docker_dir = OUTPUT_DOCKER_DIR / tool_id
            docker_dir_str = str(docker_dir)
            if len(docker_dir_str) > 50:
                docker_dir_str = "..." + docker_dir_str[-47:]
            print(f"   │ Docker directory: {docker_dir_str:<53} │")
            
            env_file = docker_dir / ".env"
            if env_file.exists():
                env_file_str = str(env_file)
                if len(env_file_str) > 50:
                    env_file_str = "..." + env_file_str[-47:]
                print(f"   │ .env file       : {env_file_str:<53} │")
            else:
                print(f"   │ .env file       : None{'':<47} │")
        else:
            print(f"   │ Docker directory: Not imported{'':<41} │")
        
        print("   └─────────────────────────────────────────────────────────────────────────┘")
    except Exception as exc:
        print(f"\n📁 FILE INFORMATION")
        print("   ┌─────────────────────────────────────────────────────────────────────────┐")
        error_str = str(exc)
        if len(error_str) > 50:
            error_str = error_str[:47] + "..."
        print(f"   │ Error getting file info: {error_str:<50} │")
        print("   └─────────────────────────────────────────────────────────────────────────┘")
