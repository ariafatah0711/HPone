"""
HPone scripts package.

This package contains command scripts for the HPone Docker template manager.
"""

from .list import (
    list_tools,
    list_enabled_tool_ids,
    list_all_enabled_tool_ids,
    list_imported_tool_ids,
    resolve_tool_dir_id
)

from .inspect import (
    inspect_tool
)

from .import_cmd import (
    import_tool
)

from .remove import (
    remove_tool
)

from .file_ops import (
    ensure_destination_dir,
    find_template_dir,
    copy_template_to_destination
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
    check_file_permissions
)

__all__ = [
    # List commands
    'list_tools',
    'list_enabled_tool_ids',
    'list_all_enabled_tool_ids',
    'list_imported_tool_ids',
    'resolve_tool_dir_id',
    
    # Inspect commands
    'inspect_tool',
    
    # Import commands
    'import_tool',
    
    # Remove commands
    'remove_tool',
    
    # File operations
    'ensure_destination_dir',
    'find_template_dir',
    'copy_template_to_destination',
    
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
    'check_file_permissions'
]
