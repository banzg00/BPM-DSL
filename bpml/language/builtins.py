"""
Built-in type definitions and mappings for BPML
Maps DSL types to target platform types (Java, TypeScript, etc.)
"""

from .custom_model import SimpleType


# Java type mappings
simple_type_java_mapper = {
    'int': 'Integer',
    'string': 'String',
    'str': 'String',
    'float': 'Float',
    'bool': 'Boolean',
    'boolean': 'Boolean',
    'long': 'Long',
    'date': 'LocalDate',
    'dateTime': 'LocalDateTime',
    'decimal': 'BigDecimal',
    'text': 'String',
}

# TypeScript type mappings
simple_type_typescript_mapper = {
    'int': 'number',
    'string': 'string',
    'str': 'string',
    'float': 'number',
    'bool': 'boolean',
    'boolean': 'boolean',
    'long': 'number',
    'date': 'Date',
    'dateTime': 'Date',
    'decimal': 'number',
    'text': 'string',
}

# Create SimpleType instances for builtins
simple_types = {key: SimpleType(None, value)
                for key, value in simple_type_java_mapper.items()}

simple_types_typescript = {key: SimpleType(None, value)
                           for key, value in simple_type_typescript_mapper.items()}
