"""
BPML (Business Process Modeling Language) Package

A comprehensive DSL for defining business processes that can generate
Spring Boot and React applications with CRUD operations and process management.

This package provides:
- TextX grammar for business process modeling (bpml.tx)
- Custom model classes for enhanced functionality (custom_model.py)
- Semantic validation and processors (processors.py)
- Utility functions for process analysis (utils.py)
- Example process definitions (examples/)

Usage:
    from textx import metamodel_from_file
    from bpml.processors import semantic_check
    from bpml.custom_model import ProcessInstance

    # Load BPML metamodel
    metamodel = metamodel_from_file('bpml.tx')
    metamodel.register_model_processor(semantic_check)

    # Parse a BPML model
    model = metamodel.model_from_file('examples/order_management.bpml')

    # Create process instance
    process = model.processes[0]
    instance = ProcessInstance(process)
    instance.start()
"""

import os
from textx import language, metamodel_from_file

__version__ = "1.0.0"
__author__ = "BPML Development Team"

# Import main components for easy access
try:
    from .processors import semantic_check
    from .custom_model import ProcessInstance, TaskInstance, ProcessAnalyzer
    from .utils import (
        ProcessAnalyzer as UtilProcessAnalyzer,
        EntityExtractor,
        FormGenerator,
        RoleHierarchyAnalyzer,
        generate_process_documentation,
        validate_process_completeness,
        estimate_process_execution_time
    )
except ImportError:
    # Handle case where modules are not yet available
    pass

__all__ = [
    'semantic_check',
    'ProcessInstance',
    'TaskInstance',
    'ProcessAnalyzer',
    'UtilProcessAnalyzer',
    'EntityExtractor',
    'FormGenerator',
    'RoleHierarchyAnalyzer',
    'generate_process_documentation',
    'validate_process_completeness',
    'estimate_process_execution_time'
]


@language('bpml', '*.bpml')
def bpml_language():
    """BPML language definition with enhanced functionality"""
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'bpml.tx'))

    # Register semantic processor for validation
    try:
        from .processors import semantic_check
        mm.register_model_processor(semantic_check)
    except ImportError:
        pass

    # Register custom model classes
    try:
        from .custom_model import SimpleType
        mm.register_scope_providers({
            '*': lambda obj: []  # Default scope provider
        })
    except ImportError:
        pass

    return mm
