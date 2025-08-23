"""
HPone scripts package.

This package contains command scripts for the HPone Docker template manager.
"""

from .list import (
    list_honeypots,
    list_enabled_honeypot_ids,
    list_all_enabled_honeypot_ids,
    list_imported_honeypot_ids,
    resolve_honeypot_dir_id
)

from .inspect import (
    inspect_honeypot
)

from .import_cmd import (
    import_honeypot
)

from .remove import (
    remove_honeypot
)

from .file_ops import (
    ensure_destination_dir,
    find_template_dir,
    copy_template_to_destination,
    remove_honeypot_data
)

from .check import (
    check_all_dependencies,
    check_python_dependencies,
    check_system_dependencies,
    print_dependency_status,
    get_installation_instructions,
    require_dependencies
)

from .error_handlers import (
    handle_yaml_error,
    handle_docker_error,
    safe_execute,
    print_error_with_suggestion,
    check_file_permissions,
    check_docker_permissions,
    check_directory_permissions
)

from .status import (
    show_status,
)

from .logs import (
    logs_main
)

from .clean import (
    clean_main,
    clean_all_honeypots,
    clean_single_honeypot
)

from .up import (
    up_main,
    up_all_honeypots,
    up_single_honeypot
)

__all__ = [
    # List commands
    'list_honeypots',
    'list_enabled_honeypot_ids',
    'list_all_enabled_honeypot_ids',
    'list_imported_honeypot_ids',
    'resolve_honeypot_dir_id',

    # Inspect commands
    'inspect_honeypot',

    # Import commands
    'import_honeypot',

    # Remove commands
    'remove_honeypot',

    # File operations
    'ensure_destination_dir',
    'find_template_dir',
    'copy_template_to_destination',
    'remove_honeypot_data',

    # Check dependencies
    'check_all_dependencies',
    'check_python_dependencies',
    'check_system_dependencies',
    'print_dependency_status',
    'get_installation_instructions',
    'require_dependencies',

    # Error handlers
    'handle_yaml_error',
    'handle_docker_error',
    'safe_execute',
    'print_error_with_suggestion',
    'check_file_permissions',
    'check_docker_permissions',
    'check_directory_permissions'
    ,
    # Status helpers
    'show_status',

    # Logs
    'logs_main',

    # Clean
    'clean_main',
    'clean_all_honeypots',
    'clean_single_honeypot',

    # Up
    'up_main',
    'up_all_honeypots',
    'up_single_honeypot'
]
