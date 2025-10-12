"""
Semantic processors and validators for BPML (Business Process Modeling Language)
These processors perform essential semantic checks on the parsed BPML models
"""

from textx import TextXSemanticError


def semantic_check(metamodel, model):
    """
    Main semantic check function that performs essential validations
    Called by TextX after parsing the model
    """
    # Collect all elements for validation
    processes = model.processes if hasattr(model, 'processes') else []

    # Perform essential validations
    _validate_project_info(model.project_info)
    _validate_processes(processes)


def _validate_project_info(project_info):
    """Validate project information"""
    if not project_info.projectName:
        raise TextXSemanticError("Project name is required")


def _validate_processes(processes):
    """Validate process definitions"""
    process_names = set()

    for process in processes:
        # Check for duplicate process names
        if process.name in process_names:
            raise TextXSemanticError(f"Duplicate process name: {process.name}")
        process_names.add(process.name)

        # Validate process structure
        _validate_process_structure(process)


def _validate_process_structure(process):
    """Validate the structure of a single process"""
    entities = process.entities if hasattr(process, 'entities') else []
    roles = process.roles if hasattr(process, 'roles') else []
    steps = process.steps if hasattr(process, 'steps') else []

    # Validate entities
    entity_names = set()
    for entity in entities:
        if entity.name in entity_names:
            raise TextXSemanticError(f"Duplicate entity name '{entity.name}' in process '{process.name}'")
        entity_names.add(entity.name)

    # Validate roles
    role_names = set()
    for role in roles:
        if role.name in role_names:
            raise TextXSemanticError(f"Duplicate role name '{role.name}' in process '{process.name}'")
        role_names.add(role.name)

    # Validate steps
    step_names = set()
    for step in steps:
        if step.name in step_names:
            raise TextXSemanticError(f"Duplicate step name '{step.name}' in process '{process.name}'")
        step_names.add(step.name)

        # Validate step references
        if step.role.name not in role_names:
            raise TextXSemanticError(f"Step '{step.name}' references unknown role '{step.role.name}' in process '{process.name}'")

        if step.entity.name not in entity_names:
            raise TextXSemanticError(f"Step '{step.name}' references unknown entity '{step.entity.name}' in process '{process.name}'")

    # Validate flow
    if hasattr(process, 'flow') and process.flow:
        _validate_flow(process.flow, step_names, process.name)


def _validate_flow(flow, valid_step_names, process_name):
    """Validate flow definition"""
    for step_ref in flow.steps:
        if step_ref.name not in valid_step_names:
            raise TextXSemanticError(f"Flow references unknown step '{step_ref.name}' in process '{process_name}'")


# Utility functions for getting model information

def get_class_name(obj):
    """Get the class name of an object"""
    return obj.__class__.__name__


def get_all_process_names(model):
    """Get all process names from the model"""
    return [process.name for process in model.processes] if hasattr(model, 'processes') else []


def get_all_entity_names(process):
    """Get all entity names from a process"""
    return [entity.name for entity in process.entities] if hasattr(process, 'entities') else []


def get_all_role_names(process):
    """Get all role names from a process"""
    return [role.name for role in process.roles] if hasattr(process, 'roles') else []
