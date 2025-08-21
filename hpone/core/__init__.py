"""
HPone Core Package

Package ini berisi core functionality untuk HPone Docker template manager.
"""

from .yaml import (
    load_tool_yaml_by_filename,
    find_tool_yaml_path,
    set_tool_enabled,
    is_tool_enabled
)

from .docker import (
    is_tool_running,
    run_compose_action,
    up_tool,
    down_tool,
    shell_tool
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
    'load_tool_yaml_by_filename',
    'find_tool_yaml_path', 
    'set_tool_enabled',
    'is_tool_enabled',
    
    # Docker operations
    'is_tool_running',
    'run_compose_action',
    'up_tool',
    'down_tool',
    'shell_tool',
    
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
