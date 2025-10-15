"""
BPML (Business Process Modeling Language) Package

A minimal DSL for defining business processes with entities, roles, and workflows.
"""

import os
from textx import language, metamodel_from_file
from .processors import semantic_check

__version__ = "0.1.0"

THIS_FOLDER = os.path.dirname(__file__)


@language('bpml', '*.bpml')
def bpml_language():
    """BPML language definition"""

    bpml_grammar_path = os.path.join(THIS_FOLDER, 'bpml.tx')

    # Simple metamodel - no custom classes or builtins needed!
    metamodel = metamodel_from_file(
        bpml_grammar_path,
        debug=False
    )

    # Register semantic validation processor
    metamodel.register_model_processor(semantic_check)

    return metamodel
