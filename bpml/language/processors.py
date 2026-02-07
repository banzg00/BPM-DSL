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
    entities = process.entities
    roles = process.roles
    states = process.states
    tasks = process.tasks

    # Validate entities
    entity_names = _validate_entities(entities, process.name)

    # Validate roles
    role_names = _validate_roles(roles, process.name)

    # Validate states
    state_names = _validate_states(states, process.name)

    # Validate tasks
    _validate_tasks(tasks, state_names, role_names, entity_names, process.name)

    # Validate transitions
    _validate_transitions(process.transitions, state_names, role_names, process.name)


def _validate_entities(entities, process_name) -> set[str]:
    """Validate entity definitions for duplicates"""
    entity_names = set()
    for entity in entities:
        if entity.name in entity_names:
            raise TextXSemanticError(
                f"Duplicate entity name '{entity.name}' in process '{process_name}'"
            )
        entity_names.add(entity.name)

    return entity_names


def _validate_roles(roles, process_name) -> set[str]:
    """Validate role hierarchy for cycles and invalid references"""
    role_names = set()
    for role in roles:
        if role.name in role_names:
            raise TextXSemanticError(
                f"Duplicate role name '{role.name}' in process '{process_name}'"
            )
        if hasattr(role, "supervised_roles") and role.supervised_roles:
            for supervised_role in role.supervised_roles:
                if supervised_role.name == role.name:
                    raise TextXSemanticError(
                        f"Role '{role.name}' cannot supervise itself in process '{process_name}'"
                    )

                if supervised_role.name not in role_names:
                    raise TextXSemanticError(
                        f"Role '{role.name}' supervises unknown role '{supervised_role.name}' in process '{process_name}'"
                    )

        role_names.add(role.name)

    return role_names


def _validate_states(states, process_name) -> set[str]:
    """Validate state definitions for duplicates"""
    state_names = set()
    for state in states:
        if state.name in state_names:
            raise TextXSemanticError(
                f"Duplicate state name '{state.name}' in process '{process_name}'"
            )
        state_names.add(state.name)

    return state_names


def _validate_tasks(
    tasks, state_names, role_names, entity_names, process_name
) -> set[str]:
    """Validate task definitions for duplicates and missing required fields"""
    task_names = set()
    for task in tasks:
        if task.name in task_names:
            raise TextXSemanticError(
                f"Duplicate task name '{task.name}' in process '{process_name}'"
            )

        # Validate state reference
        if task.state and task.state.name not in state_names:
            raise TextXSemanticError(
                f"Task '{task.name}' references unknown state '{task.state.name}' in process '{process_name}'"
            )

        # Validate that task has either a role or is automated (not both, not neither)
        is_auto = hasattr(task, "auto") and task.auto
        has_role = hasattr(task, "role") and task.role

        if (not is_auto and not has_role) or (is_auto and has_role):
            raise TextXSemanticError(
                f"Task '{task.name}' must be either automated (use 'auto') or assigned to a role (use 'by RoleName') in process '{process_name}'"
            )

        # Validate role references
        if has_role and task.role.name not in role_names:
            raise TextXSemanticError(
                f"Task '{task.name}' references unknown role '{task.role.name}' in process '{process_name}'"
            )

        # Validate entities
        if hasattr(task, "entities") and task.entities:
            for entity in task.entities:
                if entity.name not in entity_names:
                    raise TextXSemanticError(
                        f"Task '{task.name}' references unknown entity '{entity.name}' in process '{process_name}'"
                    )

        # Validate dependencies
        if hasattr(task, "dependencies") and task.dependencies:
            for dep_task in task.dependencies:
                if dep_task.name == task.name:
                    raise TextXSemanticError(
                        f"Task '{task.name}' cannot depend on itself in process '{process_name}'"
                    )
                if dep_task.name not in task_names:
                    raise TextXSemanticError(
                        f"Task '{task.name}' depends on unknown task '{dep_task.name}' in process '{process_name}'"
                    )

        task_names.add(task.name)

    return task_names


def _validate_transitions(transitions, state_names, role_names, process_name):
    """Validate transition definitions"""
    transition_names = set()
    for transition in transitions:
        if transition.name in transition_names:
            raise TextXSemanticError(
                f"Duplicate transition name '{transition.name}' in process '{process_name}'"
            )

        if transition.from_state.name not in state_names:
            raise TextXSemanticError(
                f"Transition '{transition.name}' references unknown from_state "
                f"'{transition.from_state.name}' in process '{process_name}'"
            )

        if transition.to_state.name not in state_names:
            raise TextXSemanticError(
                f"Transition '{transition.name}' references unknown to_state "
                f"'{transition.to_state.name}' in process '{process_name}'"
            )

        if transition.from_state.name == transition.to_state.name:
            raise TextXSemanticError(
                f"Transition '{transition.name}' has same from and to state "
                f"'{transition.from_state.name}' in process '{process_name}'"
            )

        if transition.role.name not in role_names:
            raise TextXSemanticError(
                f"Transition '{transition.name}' references unknown role "
                f"'{transition.role.name}' in process '{process_name}'"
            )

        transition_names.add(transition.name)
