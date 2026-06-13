"""
FlowGen Package

A minimal DSL for defining business processes with entities, roles, and workflows.
"""

import os

from textx import language, metamodel_from_file

from .processors import semantic_check

__version__ = "0.1.0"

THIS_FOLDER = os.path.dirname(__file__)


@language("flg", "*.flg")
def flg_language():
    """FlowGen language definition"""

    flg_grammar_path = os.path.join(THIS_FOLDER, "flg.tx")

    # Simple metamodel - no custom classes or builtins needed!
    metamodel = metamodel_from_file(flg_grammar_path, debug=False)

    # Register semantic validation processor
    metamodel.register_model_processor(semantic_check)

    return metamodel
