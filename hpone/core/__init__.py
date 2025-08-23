"""
HPone Core Package

Package ini berisi core functionality untuk HPone Docker template manager.
"""

from .yaml import (
    load_honeypot_yaml_by_filename,
    find_honeypot_yaml_path,
    set_honeypot_enabled,
    is_honeypot_enabled
)

from .docker import (
    is_honeypot_running,
    run_compose_action,
    up_honeypot,
    down_honeypot,
    shell_honeypot
)

from .config import (
    parse_ports,
    parse_volumes,
    parse_env,
    normalize_host_path,
    generate_env_file,
    ensure_volume_directories,
    rewrite_compose_with_env
)

from .utils import (
    to_var_prefix,
    _format_table
)

from .log_runner import (
    run_with_ephemeral_logs,
    run_docker_compose_action
)

__all__ = [
    # YAML operations
    'load_honeypot_yaml_by_filename',
    'find_honeypot_yaml_path',
    'set_honeypot_enabled',
    'is_honeypot_enabled',

    # Docker operations
    'is_honeypot_running',
    'run_compose_action',
    'up_honeypot',
    'down_honeypot',
    'shell_honeypot',

    # Configuration handling
    'parse_ports',
    'parse_volumes',
    'parse_env',
    'normalize_host_path',
    'generate_env_file',
    'ensure_volume_directories',
    'rewrite_compose_with_env',

    # Utility functions
    'to_var_prefix',
    '_format_table',

    # Log runner functions
    'run_with_ephemeral_logs',
    'run_docker_compose_action'
]
