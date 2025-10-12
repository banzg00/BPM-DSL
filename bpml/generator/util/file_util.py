"""
File utility functions for BPML generator
Handles output directory creation and path management
"""

import os


def create_output_file(output_path, generated_folder_name):
    """Create output directory for generated files"""
    if output_path is None:
        output_path = os.getcwd()
    output_path = os.path.join(output_path, generated_folder_name, '')
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)
    return output_path


def get_main_java_folder_path(output_path, context):
    """Get path to main Java source folder"""
    return os.path.join(
        output_path,
        context['app_name_lower'],
        'src/main/java',
        context['group_name'].replace('.', '/'),
        context['app_name_lower']
    )


def get_resources_folder_path(output_path, context):
    """Get path to Spring Boot resources folder"""
    return os.path.join(
        output_path,
        context['app_name_lower'],
        'src/main/resources'
    )


def get_react_components_folder_path(output_path, context):
    """Get path to React components folder"""
    return os.path.join(output_path, 'src/components')


def get_react_pages_folder_path(output_path, context):
    """Get path to React pages folder"""
    return os.path.join(output_path, 'src/pages')


def format_template_name(path):
    """Extract template name from path"""
    return os.path.split(path)[-1]
