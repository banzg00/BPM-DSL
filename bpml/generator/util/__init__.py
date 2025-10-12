"""
Utility functions for BPML code generation
"""

from .file_util import (
    create_output_file,
    get_main_java_folder_path,
    get_resources_folder_path,
    get_react_components_folder_path,
    get_react_pages_folder_path,
    format_template_name
)

from .string_format_util import (
    dash_case,
    snake_case,
    capitalize_str,
    lower_first_str,
    camel_case,
    pascal_case,
    upper_case
)

from .filters import (
    format_type_java,
    format_type_typescript,
    is_enum_type,
    get_enum_values,
    is_simple_type
)

__all__ = [
    # File utilities
    'create_output_file',
    'get_main_java_folder_path',
    'get_resources_folder_path',
    'get_react_components_folder_path',
    'get_react_pages_folder_path',
    'format_template_name',
    # String formatting
    'dash_case',
    'snake_case',
    'capitalize_str',
    'lower_first_str',
    'camel_case',
    'pascal_case',
    'upper_case',
    # Type filters
    'format_type_java',
    'format_type_typescript',
    'is_enum_type',
    'get_enum_values',
    'is_simple_type'
]
