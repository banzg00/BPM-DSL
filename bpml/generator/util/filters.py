"""
Jinja2 filter functions for BPML generator
Provides type mapping and data type conversion for templates
"""

from bpml.language.builtins import data_type_java_mapper, data_type_typescript_mapper


def format_type_java(obj_type):
    """Convert BPML type to Java type
    Example: string -> String, int -> Integer
    """
    type_name = obj_type if isinstance(obj_type, str) else str(obj_type)
    return data_type_java_mapper.get(type_name, type_name)


def format_type_typescript(obj_type):
    """Convert BPML type to TypeScript type
    Example: string -> string, int -> number
    """
    type_name = obj_type if isinstance(obj_type, str) else str(obj_type)
    return data_type_typescript_mapper.get(type_name, type_name)


def is_enum_type(data_type):
    """Check if data type is an enum"""
    return data_type.__class__.__name__ == "Enum"


def get_enum_values(enum_type):
    """Extract enum values from enum definition"""
    if hasattr(enum_type, "values"):
        return enum_type.values
    return []


def is_simple_type(data_type):
    """Check if data type is a simple type (not enum)"""
    type_str = str(data_type)
    return type_str in data_type_java_mapper.keys()
