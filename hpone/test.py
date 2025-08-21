#!/usr/bin/env python3
"""
Self-test utilities for HPone.

This module provides a function to verify that key package imports
work correctly before running dependency checks.
"""

from __future__ import annotations
from core.utils import PREFIX_ERROR

def run_import_self_test() -> bool:
    """Run a quick self-test to ensure key imports work.

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
        "load_tool_yaml_by_filename",
        "find_tool_yaml_path",
        "set_tool_enabled",
        "is_tool_enabled",
        "is_tool_running",
        "run_compose_action",
        "up_tool",
        "down_tool",
        "parse_ports",
        "parse_volumes",
        "parse_env",
        "normalize_host_path",
        "generate_env_file",
        "ensure_volume_directories",
        "rewrite_compose_with_env",
        "to_var_prefix",
        "_format_table",
    ]
    for name in core_functions:
        expr = f"from core import {name}"
        if _try_exec(expr):
            success_count += 1
        else:
            fail_count += 1

    # Scripts exports via package __init__
    scripts_functions = [
        "list_tools",
        "list_enabled_tool_ids",
        "list_all_enabled_tool_ids",
        "list_imported_tool_ids",
        "resolve_tool_dir_id",
        "inspect_tool",
        "import_tool",
        "ensure_destination_dir",
        "find_template_dir",
        "copy_template_to_destination",
        "remove_tool",
        "require_dependencies",
        "show_status",
    ]
    for name in scripts_functions:
        expr = f"from scripts import {name}"
        if _try_exec(expr):
            success_count += 1
        else:
            fail_count += 1

    # Core constants direct import
    constant_names = [
        "TOOLS_DIR",
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

    total = success_count + fail_count
    print(f"Import self-test: {success_count}/{total} passed")
    return fail_count == 0