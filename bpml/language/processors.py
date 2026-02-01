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
    processes = metamodel.processes if hasattr(metamodel, "processes") else []

    # Perform essential validations
    _validate_project_info(metamodel.project_info)
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
    entities = process.entities if hasattr(process, "entities") else []
    roles = process.roles if hasattr(process, "roles") else []
    states = process.states if hasattr(process, "states") else []
    tasks = process.tasks if hasattr(process, "tasks") else []

    # Validate entities
    entity_names = set()
    for entity in entities:
        if entity.name in entity_names:
            raise TextXSemanticError(
                f"Duplicate entity name '{entity.name}' in process '{process.name}'"
            )
        entity_names.add(entity.name)

    # Validate roles
    role_names = set()
    for role in roles:
        if role.name in role_names:
            raise TextXSemanticError(
                f"Duplicate role name '{role.name}' in process '{process.name}'"
            )
        role_names.add(role.name)

    # Validate role hierarchy
    _validate_role_hierarchy(roles, process.name)

    # Validate states
    state_names = set()
    for state in states:
        if state.name in state_names:
            raise TextXSemanticError(
                f"Duplicate state name '{state.name}' in process '{process.name}'"
            )
        state_names.add(state.name)

    # Validate tasks
    task_names = set()
    for task in tasks:
        if task.name in task_names:
            raise TextXSemanticError(
                f"Duplicate task name '{task.name}' in process '{process.name}'"
            )
        task_names.add(task.name)

        # Validate state reference
        if task.state and task.state.name not in state_names:
            raise TextXSemanticError(
                f"Task '{task.name}' references unknown state '{task.state.name}' in process '{process.name}'"
            )

        # Validate that task has either a role or is automated (not both, not neither)
        is_auto = hasattr(task, 'auto') and task.auto
        has_role = hasattr(task, 'role') and task.role

        if not is_auto and not has_role:
            raise TextXSemanticError(
                f"Task '{task.name}' must be either automated (use 'auto') or assigned to a role (use 'by RoleName') in process '{process.name}'"
            )

        # Validate role references
        if has_role and task.role.name not in role_names:
            raise TextXSemanticError(
                f"Task '{task.name}' references unknown role '{task.role.name}' in process '{process.name}'"
            )

        # Validate entities (now optional and plural)
        if hasattr(task, 'entities') and task.entities:
            for entity in task.entities:
                if entity.name not in entity_names:
                    raise TextXSemanticError(
                        f"Task '{task.name}' references unknown entity '{entity.name}' in process '{process.name}'"
                    )

        # Validate dependencies (optional)
        if hasattr(task, 'dependencies') and task.dependencies:
            for dep_task in task.dependencies:
                if dep_task.name not in task_names:
                    raise TextXSemanticError(
                        f"Task '{task.name}' depends on unknown task '{dep_task.name}' in process '{process.name}'"
                    )

    # Validate task dependencies for cycles
    _validate_task_dependencies(tasks, process.name)

    # Validate flow
    if hasattr(process, "flow") and process.flow:
        _validate_flow(process.flow, task_names, process.name)


def _validate_task_dependencies(tasks, process_name):
    """Validate task dependencies for circular references"""
    def has_cycle(task, visited, rec_stack, task_map):
        """DFS to detect cycles in task dependencies"""
        visited.add(task.name)
        rec_stack.add(task.name)

        if hasattr(task, 'dependencies') and task.dependencies:
            for dep_task in task.dependencies:
                dep_name = dep_task.name
                if dep_name not in visited:
                    if has_cycle(task_map[dep_name], visited, rec_stack, task_map):
                        return True
                elif dep_name in rec_stack:
                    return True

        rec_stack.remove(task.name)
        return False

    # Build task name to task object map
    task_map = {task.name: task for task in tasks}

    # Check for cycles starting from each task
    visited = set()
    for task in tasks:
        if task.name not in visited:
            rec_stack = set()
            if has_cycle(task, visited, rec_stack, task_map):
                raise TextXSemanticError(
                    f"Circular dependency detected in task dependencies in process '{process_name}'"
                )


def _validate_flow(flow, valid_task_names, process_name):
    """Validate flow definition"""
    for task_ref in flow.tasks:
        if task_ref.name not in valid_task_names:
            raise TextXSemanticError(
                f"Flow references unknown task '{task_ref.name}' in process '{process_name}'"
            )


def _validate_role_hierarchy(roles, process_name):
    """Validate role hierarchy for cycles and invalid references"""
    role_names = {role.name for role in roles}

    for role in roles:
        # Check if role has supervised roles
        if hasattr(role, 'supervised_roles') and role.supervised_roles:
            # Validate supervised role references exist
            for supervised_role in role.supervised_roles:
                if supervised_role.name not in role_names:
                    raise TextXSemanticError(
                        f"Role '{role.name}' supervises unknown role '{supervised_role.name}' in process '{process_name}'"
                    )

            # Check for self-supervision
            supervised_names = {r.name for r in role.supervised_roles}
            if role.name in supervised_names:
                raise TextXSemanticError(
                    f"Role '{role.name}' cannot supervise itself in process '{process_name}'"
                )


# Utility functions for getting model information


def get_class_name(obj):
    """Get the class name of an object"""
    return obj.__class__.__name__


def get_all_process_names(model):
    """Get all process names from the model"""
    return (
        [process.name for process in model.processes]
        if hasattr(model, "processes")
        else []
    )


def get_all_entity_names(process):
    """Get all entity names from a process"""
    return (
        [entity.name for entity in process.entities]
        if hasattr(process, "entities")
        else []
    )


def get_all_role_names(process):
    """Get all role names from a process"""
    return [role.name for role in process.roles] if hasattr(process, "roles") else []
