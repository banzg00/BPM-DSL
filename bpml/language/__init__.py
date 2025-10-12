"""
BPML (Business Process Modeling Language) Package

A minimal DSL for defining business processes with entities, roles, and workflows.
"""

import os
from textx import language, metamodel_from_file
from .custom_model import SimpleType, DataType
from .builtins import simple_types
from .processors import semantic_check

__version__ = "0.1.0"

THIS_FOLDER = os.path.dirname(__file__)


def get_custom_classes():
    """Return list of custom model classes to register with TextX"""
    return [SimpleType, DataType]


@language('bpml', '*.bpml')
def bpml_language():
    """BPML language definition"""

    bpml_grammar_path = os.path.join(THIS_FOLDER, 'bpml.tx')

    metamodel = metamodel_from_file(
        bpml_grammar_path,
        classes=get_custom_classes(),
        builtins=simple_types,
        debug=False
    )

    # Register semantic validation processor
    metamodel.register_model_processor(semantic_check)

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/

    return metamodel
