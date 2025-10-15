"""
Built-in type definitions and mappings for BPML
Maps DSL types to target platform types (Java, TypeScript, etc.)
"""

from .custom_model import DataType

# Java type mappings
data_type_java_mapper = {
    "int": "Integer",
    "string": "String",
    "float": "Float",
    "boolean": "Boolean",
}

# TypeScript type mappings
data_type_typescript_mapper = {
    "int": "number",
    "string": "string",
    "float": "number",
    "boolean": "boolean",
}

# Create DataType instances for builtins
data_types_java = {
    key: DataType(None, value) for key, value in data_type_java_mapper.items()
}

data_types_typescript = {
    key: DataType(None, value) for key, value in data_type_typescript_mapper.items()
}
