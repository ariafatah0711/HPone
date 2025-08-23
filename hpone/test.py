#!/usr/bin/env python3
"""
Self-test utilities for HPone.

This module provides comprehensive testing of internal package imports including:
- Core module functions and utilities
- All scripts module functions (including clean and up commands)
- Constants and configuration imports

This ensures all internal module imports work correctly. External dependency
checking is handled separately by the dependency checking system.
"""

from __future__ import annotations
from core.utils import PREFIX_ERROR

def run_import_self_test() -> bool:
    """Run a quick self-test to ensure internal module imports work.

    Tests all core and scripts module imports to verify package structure.
    External dependencies are checked separately by the dependency system.

    Returns True if all checks pass, False otherwise.
    """
    print("Running import self-tests...")
    success_count = 0
    fail_count = 0

    def _try_exec(expr: str) -> bool:
        try:
            exec(expr, globals(), {})
            return True
        except Exception as exc:  # noqa: BLE001 - report to user
            print(f"{PREFIX_ERROR} {expr} -> {exc}")
            return False

    # Core exports via package __init__
    core_functions = [
        "load_honeypot_yaml_by_filename",
        "find_honeypot_yaml_path",
        "set_honeypot_enabled",
        "is_honeypot_enabled",
        "get_custom_template_dir",
        "is_honeypot_running",
        "run_compose_action",
        "up_honeypot",
        "down_honeypot",
        "shell_honeypot",
        "cleanup_global_images",
        "cleanup_global_volumes",
        "parse_ports",
        "parse_ports_with_description",
        "parse_volumes",
        "parse_env",
        "normalize_host_path",
        "generate_env_file",
        "ensure_volume_directories",
        "rewrite_compose_with_env",
        "to_var_prefix",
        "_format_table",
        "run_with_ephemeral_logs",
        "run_docker_compose_action",
    ]
    for name in core_functions:
        expr = f"from core import {name}"
        if _try_exec(expr):
            success_count += 1
        else:
            fail_count += 1

    # Scripts exports via package __init__
    scripts_functions = [
        "list_honeypots",
        "list_enabled_honeypot_ids",
        "list_all_enabled_honeypot_ids",
        "list_imported_honeypot_ids",
        "resolve_honeypot_dir_id",
        "inspect_honeypot",
        "import_honeypot",
        "remove_honeypot",
        "ensure_destination_dir",
        "find_template_dir",
        "copy_template_to_destination",
        "remove_honeypot_data",
        "check_all_dependencies",
        "check_python_dependencies",
        "check_system_dependencies",
        "print_dependency_status",
        "get_installation_instructions",
        "require_dependencies",
        "handle_yaml_error",
        "handle_docker_error",
        "safe_execute",
        "print_error_with_suggestion",
        "check_file_permissions",
        "show_status",
        "logs_main",
        "clean_main",
        "clean_all_honeypots",
        "clean_single_honeypot",
        "up_main",
        "up_all_honeypots",
        "up_single_honeypot",
    ]
    for name in scripts_functions:
        expr = f"from scripts import {name}"
        if _try_exec(expr):
            success_count += 1
        else:
            fail_count += 1

    # Core constants direct import
    constant_names = [
        "HONEYPOT_MANIFEST_DIR",
        "TEMPLATE_DOCKER_DIR",
        "OUTPUT_DOCKER_DIR",
        "DATA_DIR",
    ]
    for const_name in constant_names:
        expr = f"from core.constants import {const_name}"
        if _try_exec(expr):
            success_count += 1
        else:
            fail_count += 1

    # Additional utility imports
    utility_imports = [
        "from core.utils import PREFIX_OK",
        "from core.utils import PREFIX_ERROR",
        "from core.utils import PREFIX_WARN",
        "from core.argaparse import build_arg_parser",
        "from core.argaparse import format_full_help",
    ]
    for expr in utility_imports:
        if _try_exec(expr):
            success_count += 1
        else:
            fail_count += 1

    # Test config import (optional)
    config_imports = [
        "from config import ALWAYS_IMPORT",
    ]
    for expr in config_imports:
        if _try_exec(expr):
            success_count += 1
        else:
            # Config imports are optional, don't count as failure
            pass

    total = success_count + fail_count
    success_rate = (success_count / total * 100) if total > 0 else 0
    print(f"Import self-test: {success_count}/{total} passed ({success_rate:.1f}%)")

    if fail_count > 0:
        print(f"{PREFIX_ERROR} {fail_count} import(s) failed. Check module structure.")

    return fail_count == 0
