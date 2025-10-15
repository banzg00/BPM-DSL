"""
Custom model classes for BPML (Business Process Modeling Language)
These classes extend the basic TextX generated model with additional functionality
"""


class DataType:
    """Data type wrapper for handling complex type references"""

    def __init__(self, parent, type_ref):
        self.parent = parent
        self.type_ref = type_ref

    def __str__(self):
        return str(self.type_ref)
