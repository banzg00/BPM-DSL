"""
Semantic processors and validators for BPML (Business Process Modeling Language)
These processors perform semantic checks and validations on the parsed BPML models
"""

from textx import TextXSemanticError
from typing import List, Set, Dict, Any
import re


def semantic_check(metamodel, model):
    """
    Main semantic check function that performs all validations
    Called by TextX after parsing the model
    """
    try:
        # Collect all elements for validation
        processes = model.processes if hasattr(model, 'processes') else []
        entities = model.entities if hasattr(model, 'entities') else []
        roles = model.roles if hasattr(model, 'roles') else []
        dashboards = model.dashboards if hasattr(model, 'dashboards') else []

        # Perform comprehensive validations
        _validate_project_info(model.project_info)
        _validate_entities(entities)
        _validate_roles(roles)
        _validate_processes(processes, entities, roles)
        _validate_dashboards(dashboards, processes)

        # Cross-model validations
        _validate_cross_references(model)

    except Exception as e:
        raise TextXSemanticError(f"Semantic validation failed: {str(e)}")


def _validate_project_info(project_info):
    """Validate project information"""
    if not project_info.projectName:
        raise TextXSemanticError("Project name is required")

    # Validate project name format
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', project_info.projectName):
        raise TextXSemanticError("Project name must start with a letter and contain only letters, numbers, and underscores")


def _validate_entities(entities):
    """Validate entity definitions"""
    entity_names = set()

    for entity in entities:
        # Check for duplicate entity names
        if entity.name in entity_names:
            raise TextXSemanticError(f"Duplicate entity name: {entity.name}")
        entity_names.add(entity.name)

        # Validate entity properties
        _validate_entity_properties(entity)


def _validate_entity_properties(entity):
    """Validate properties within an entity"""
    property_names = set()

    for prop in entity.properties:
        # Check for duplicate property names
        if prop.name in property_names:
            raise TextXSemanticError(f"Duplicate property name '{prop.name}' in entity '{entity.name}'")
        property_names.add(prop.name)

        # Validate property type and constraints
        _validate_property_definition(prop, entity.name)


def _validate_property_definition(prop, entity_name):
    """Validate individual property definition"""
    prop_type = prop.__class__.__name__

    if prop_type == 'Attribute':
        _validate_attribute(prop, entity_name)
    elif prop_type == 'Relationship':
        _validate_relationship(prop, entity_name)


def _validate_attribute(attribute, entity_name):
    """Validate attribute definition"""
    # Check if type is valid SimpleType
    valid_types = {'int', 'str', 'float', 'bool', 'long', 'dateTime', 'date',
                   'decimal', 'text', 'email', 'phone', 'url'}

    if hasattr(attribute.type, 'name') and attribute.type.name not in valid_types:
        raise TextXSemanticError(f"Invalid attribute type '{attribute.type.name}' for attribute '{attribute.name}' in entity '{entity_name}'")


def _validate_relationship(relationship, entity_name):
    """Validate relationship definition"""
    # Validate cardinality
    valid_cardinalities = {'@1..1', '@1..*', '@*..1', '@*..*', '@0..1', '@0..*'}

    if relationship.cardinality not in valid_cardinalities:
        raise TextXSemanticError(f"Invalid cardinality '{relationship.cardinality}' for relationship '{relationship.name}' in entity '{entity_name}'")


def _validate_roles(roles):
    """Validate role definitions"""
    role_names = set()

    for role in roles:
        # Check for duplicate role names
        if role.name in role_names:
            raise TextXSemanticError(f"Duplicate role name: {role.name}")
        role_names.add(role.name)

        # Validate role hierarchy
        _validate_role_hierarchy(role, roles)


def _validate_role_hierarchy(role, all_roles):
    """Validate role inheritance hierarchy"""
    if hasattr(role, 'parent') and role.parent:
        # Check for circular inheritance
        visited = set()
        current = role

        while current and hasattr(current, 'parent') and current.parent:
            if current.name in visited:
                raise TextXSemanticError(f"Circular inheritance detected in role hierarchy starting from '{role.name}'")
            visited.add(current.name)
            current = current.parent


def _validate_processes(processes, entities, roles):
    """Validate process definitions"""
    process_names = set()

    for process in processes:
        # Check for duplicate process names
        if process.name in process_names:
            raise TextXSemanticError(f"Duplicate process name: {process.name}")
        process_names.add(process.name)

        # Validate process structure
        _validate_process_structure(process, entities, roles)


def _validate_process_structure(process, entities, roles):
    """Validate the structure of a single process"""
    elements = process.elements if hasattr(process, 'elements') else []

    # Check for required start and end events
    start_events = [e for e in elements if e.__class__.__name__ == 'StartEvent']
    end_events = [e for e in elements if e.__class__.__name__ == 'EndEvent']

    if not start_events:
        raise TextXSemanticError(f"Process '{process.name}' must have at least one start event")

    if not end_events:
        raise TextXSemanticError(f"Process '{process.name}' must have at least one end event")

    # Validate individual elements
    element_names = set()
    for element in elements:
        # Check for duplicate element names
        if element.name in element_names:
            raise TextXSemanticError(f"Duplicate element name '{element.name}' in process '{process.name}'")
        element_names.add(element.name)

        # Validate specific element types
        _validate_process_element(element, process.name, entities, roles)

    # Validate sequence flows if present
    if hasattr(process, 'flows') and process.flows:
        _validate_sequence_flows(process.flows, elements, process.name)

    # Validate process connectivity
    _validate_process_connectivity(process)


def _validate_process_element(element, process_name, entities, roles):
    """Validate individual process elements"""
    element_type = element.__class__.__name__

    if element_type == 'UserTask':
        _validate_user_task(element, process_name, roles)
    elif element_type == 'ServiceTask':
        _validate_service_task(element, process_name)
    elif element_type == 'ScriptTask':
        _validate_script_task(element, process_name)
    elif element_type in ['ExclusiveGateway', 'InclusiveGateway']:
        _validate_conditional_gateway(element, process_name)
    elif element_type == 'ParallelGateway':
        _validate_parallel_gateway(element, process_name)
    elif element_type == 'DataObject':
        _validate_data_object(element, process_name, entities)


def _validate_user_task(user_task, process_name, roles):
    """Validate user task definition"""
    # Validate assignee
    if hasattr(user_task, 'assignee') and user_task.assignee:
        _validate_task_assignee(user_task.assignee, user_task.name, process_name, roles)

    # Validate candidate groups
    if hasattr(user_task, 'candidateGroups') and user_task.candidateGroups:
        role_names = {role.name for role in roles}
        for group in user_task.candidateGroups:
            if group.name not in role_names:
                raise TextXSemanticError(f"Unknown role '{group.name}' in candidate groups for task '{user_task.name}' in process '{process_name}'")

    # Validate form definition
    if hasattr(user_task, 'form') and user_task.form:
        _validate_form_definition(user_task.form, user_task.name, process_name)

    # Validate priority
    if hasattr(user_task, 'priority') and user_task.priority:
        valid_priorities = {'low', 'normal', 'high', 'critical'}
        if user_task.priority not in valid_priorities:
            raise TextXSemanticError(f"Invalid priority '{user_task.priority}' for task '{user_task.name}' in process '{process_name}'")


def _validate_task_assignee(assignee, task_name, process_name, roles):
    """Validate task assignee definition"""
    assignee_type = assignee.__class__.__name__

    if assignee_type == 'RoleAssignee':
        role_names = {role.name for role in roles}
        if assignee.role.name not in role_names:
            raise TextXSemanticError(f"Unknown role '{assignee.role.name}' assigned to task '{task_name}' in process '{process_name}'")

    elif assignee_type == 'ExpressionAssignee':
        # Basic expression validation
        if not assignee.expression or len(assignee.expression.strip()) == 0:
            raise TextXSemanticError(f"Empty assignee expression for task '{task_name}' in process '{process_name}'")


def _validate_service_task(service_task, process_name):
    """Validate service task definition"""
    if not hasattr(service_task, 'implementation') or not service_task.implementation:
        raise TextXSemanticError(f"Service task '{service_task.name}' in process '{process_name}' must have implementation defined")

    # Validate retry count if present
    if hasattr(service_task, 'retryCount') and service_task.retryCount is not None:
        if service_task.retryCount < 0:
            raise TextXSemanticError(f"Retry count cannot be negative for service task '{service_task.name}' in process '{process_name}'")

    # Validate timeout if present
    if hasattr(service_task, 'timeout') and service_task.timeout is not None:
        if service_task.timeout <= 0:
            raise TextXSemanticError(f"Timeout must be positive for service task '{service_task.name}' in process '{process_name}'")


def _validate_script_task(script_task, process_name):
    """Validate script task definition"""
    if not hasattr(script_task, 'script') or not script_task.script:
        raise TextXSemanticError(f"Script task '{script_task.name}' in process '{process_name}' must have script defined")

    # Validate script language if present
    if hasattr(script_task, 'scriptLanguage') and script_task.scriptLanguage:
        valid_languages = {'javascript', 'groovy', 'python'}
        if script_task.scriptLanguage not in valid_languages:
            raise TextXSemanticError(f"Invalid script language '{script_task.scriptLanguage}' for script task '{script_task.name}' in process '{process_name}'")


def _validate_conditional_gateway(gateway, process_name):
    """Validate conditional gateways (exclusive/inclusive)"""
    if not hasattr(gateway, 'conditions') or not gateway.conditions:
        raise TextXSemanticError(f"Gateway '{gateway.name}' in process '{process_name}' must have at least one condition")

    # Validate condition expressions
    for condition in gateway.conditions:
        if not condition.condition or len(condition.condition.strip()) == 0:
            raise TextXSemanticError(f"Empty condition in gateway '{gateway.name}' in process '{process_name}'")


def _validate_parallel_gateway(gateway, process_name):
    """Validate parallel gateway definition"""
    # Validate join type if present
    if hasattr(gateway, 'joinType') and gateway.joinType:
        valid_join_types = {'all', 'any', 'majority'}
        if gateway.joinType not in valid_join_types:
            raise TextXSemanticError(f"Invalid join type '{gateway.joinType}' for parallel gateway '{gateway.name}' in process '{process_name}'")


def _validate_data_object(data_object, process_name, entities):
    """Validate data object definition"""
    # Validate data type
    if hasattr(data_object, 'dataType') and data_object.dataType:
        _validate_data_type(data_object.dataType, data_object.name, process_name, entities)

    # Validate scope
    if hasattr(data_object, 'scope') and data_object.scope:
        valid_scopes = {'process', 'global', 'task'}
        if data_object.scope not in valid_scopes:
            raise TextXSemanticError(f"Invalid scope '{data_object.scope}' for data object '{data_object.name}' in process '{process_name}'")


def _validate_data_type(data_type, object_name, process_name, entities):
    """Validate data type definition"""
    data_type_class = data_type.__class__.__name__

    if data_type_class == 'EntityType':
        entity_names = {entity.name for entity in entities}
        if data_type.entity.name not in entity_names:
            raise TextXSemanticError(f"Unknown entity '{data_type.entity.name}' referenced in data object '{object_name}' in process '{process_name}'")


def _validate_form_definition(form, task_name, process_name):
    """Validate form definition"""
    if not hasattr(form, 'fields') or not form.fields:
        raise TextXSemanticError(f"Form for task '{task_name}' in process '{process_name}' must have at least one field")

    field_names = set()
    for field in form.fields:
        # Check for duplicate field names
        if field.name in field_names:
            raise TextXSemanticError(f"Duplicate field name '{field.name}' in form for task '{task_name}' in process '{process_name}'")
        field_names.add(field.name)

        # Validate field type
        _validate_form_field_type(field, task_name, process_name)

    # Validate form validations if present
    if hasattr(form, 'validations') and form.validations:
        _validate_form_validations(form.validations, field_names, task_name, process_name)


def _validate_form_field_type(field, task_name, process_name):
    """Validate form field type"""
    valid_field_types = {
        'text', 'number', 'email', 'password', 'textarea', 'select', 'multiselect',
        'checkbox', 'radio', 'date', 'datetime', 'file', 'bool', 'entity'
    }

    if field.fieldType not in valid_field_types:
        raise TextXSemanticError(f"Invalid field type '{field.fieldType}' for field '{field.name}' in form for task '{task_name}' in process '{process_name}'")


def _validate_form_validations(validations, field_names, task_name, process_name):
    """Validate form validation rules"""
    for validation in validations:
        # Check if referenced field exists
        if validation.field.name not in field_names:
            raise TextXSemanticError(f"Validation references unknown field '{validation.field.name}' in form for task '{task_name}' in process '{process_name}'")

        # Validate validation type
        valid_validation_types = {'required', 'minLength', 'maxLength', 'pattern', 'min', 'max', 'email', 'custom'}
        if validation.validationType not in valid_validation_types:
            raise TextXSemanticError(f"Invalid validation type '{validation.validationType}' for field '{validation.field.name}' in form for task '{task_name}' in process '{process_name}'")


def _validate_sequence_flows(flows, elements, process_name):
    """Validate sequence flows"""
    element_names = {element.name for element in elements}

    for flow in flows:
        # Check if source and target elements exist
        if flow.source.name not in element_names:
            raise TextXSemanticError(f"Sequence flow references unknown source element '{flow.source.name}' in process '{process_name}'")

        if flow.target.name not in element_names:
            raise TextXSemanticError(f"Sequence flow references unknown target element '{flow.target.name}' in process '{process_name}'")

        # Validate flow conditions if present
        if hasattr(flow, 'condition') and flow.condition:
            if not flow.condition.strip():
                raise TextXSemanticError(f"Empty condition in sequence flow from '{flow.source.name}' to '{flow.target.name}' in process '{process_name}'")


def _validate_process_connectivity(process):
    """Validate that process elements are properly connected"""
    if not hasattr(process, 'elements') or not process.elements:
        return

    elements = process.elements
    flows = process.flows if hasattr(process, 'flows') and process.flows else []

    # Build connectivity graph
    outgoing = {}
    incoming = {}

    for element in elements:
        element_name = element.name
        outgoing[element_name] = []
        incoming[element_name] = []

    for flow in flows:
        source_name = flow.source.name
        target_name = flow.target.name
        outgoing[source_name].append(target_name)
        incoming[target_name].append(source_name)

    # Check connectivity rules
    for element in elements:
        element_type = element.__class__.__name__
        element_name = element.name

        # Start events should have no incoming flows
        if element_type == 'StartEvent' and incoming[element_name]:
            raise TextXSemanticError(f"Start event '{element_name}' cannot have incoming flows in process '{process.name}'")

        # End events should have no outgoing flows
        if element_type == 'EndEvent' and outgoing[element_name]:
            raise TextXSemanticError(f"End event '{element_name}' cannot have outgoing flows in process '{process.name}'")

        # Other elements should have both incoming and outgoing flows (except start/end)
        if element_type not in ['StartEvent', 'EndEvent']:
            if not incoming[element_name]:
                raise TextXSemanticError(f"Element '{element_name}' has no incoming flows in process '{process.name}'")
            if not outgoing[element_name]:
                raise TextXSemanticError(f"Element '{element_name}' has no outgoing flows in process '{process.name}'")


def _validate_dashboards(dashboards, processes):
    """Validate dashboard definitions"""
    dashboard_names = set()
    process_names = {process.name for process in processes}

    for dashboard in dashboards:
        # Check for duplicate dashboard names
        if dashboard.name in dashboard_names:
            raise TextXSemanticError(f"Duplicate dashboard name: {dashboard.name}")
        dashboard_names.add(dashboard.name)

        # Validate dashboard widgets
        if hasattr(dashboard, 'widgets') and dashboard.widgets:
            _validate_dashboard_widgets(dashboard.widgets, dashboard.name, process_names)


def _validate_dashboard_widgets(widgets, dashboard_name, process_names):
    """Validate dashboard widgets"""
    for widget in widgets:
        widget_type = widget.__class__.__name__

        if widget_type == 'ProcessInstanceList':
            _validate_process_instance_list_widget(widget, dashboard_name)
        elif widget_type == 'TaskList':
            _validate_task_list_widget(widget, dashboard_name)
        elif widget_type == 'ProcessMetrics':
            _validate_process_metrics_widget(widget, dashboard_name)
        elif widget_type == 'CustomChart':
            _validate_custom_chart_widget(widget, dashboard_name)


def _validate_process_instance_list_widget(widget, dashboard_name):
    """Validate process instance list widget"""
    if not hasattr(widget, 'columns') or not widget.columns:
        raise TextXSemanticError(f"Process instance list widget in dashboard '{dashboard_name}' must have columns defined")


def _validate_task_list_widget(widget, dashboard_name):
    """Validate task list widget"""
    if not hasattr(widget, 'actions') or not widget.actions:
        raise TextXSemanticError(f"Task list widget in dashboard '{dashboard_name}' must have actions defined")

    # Validate action types
    valid_actions = {'complete', 'delegate', 'claim', 'release', 'view', 'edit', 'delete', 'start'}
    for action in widget.actions:
        if action not in valid_actions:
            raise TextXSemanticError(f"Invalid action '{action}' in task list widget in dashboard '{dashboard_name}'")


def _validate_process_metrics_widget(widget, dashboard_name):
    """Validate process metrics widget"""
    if not hasattr(widget, 'charts') or not widget.charts:
        raise TextXSemanticError(f"Process metrics widget in dashboard '{dashboard_name}' must have charts defined")

    # Validate chart types
    valid_charts = {
        'averageProcessTime', 'tasksCompletedToday', 'processInstancesByStatus',
        'tasksByAssignee', 'overdueTasks', 'processThroughput'
    }
    for chart in widget.charts:
        if chart not in valid_charts:
            raise TextXSemanticError(f"Invalid chart type '{chart}' in process metrics widget in dashboard '{dashboard_name}'")


def _validate_custom_chart_widget(widget, dashboard_name):
    """Validate custom chart widget"""
    if not hasattr(widget, 'chartType') or not widget.chartType:
        raise TextXSemanticError(f"Custom chart widget '{widget.name}' in dashboard '{dashboard_name}' must have chart type defined")

    valid_chart_types = {'line', 'bar', 'pie', 'donut', 'area', 'scatter'}
    if widget.chartType not in valid_chart_types:
        raise TextXSemanticError(f"Invalid chart type '{widget.chartType}' for custom chart widget '{widget.name}' in dashboard '{dashboard_name}'")

    if not hasattr(widget, 'dataSource') or not widget.dataSource:
        raise TextXSemanticError(f"Custom chart widget '{widget.name}' in dashboard '{dashboard_name}' must have data source defined")


def _validate_cross_references(model):
    """Validate cross-references between different model elements"""
    # This function performs validations that span across different sections of the model

    # Collect all defined names for reference validation
    entity_names = {entity.name for entity in model.entities} if hasattr(model, 'entities') else set()
    role_names = {role.name for role in model.roles} if hasattr(model, 'roles') else set()
    process_names = {process.name for process in model.processes} if hasattr(model, 'processes') else set()

    # Validate entity references in relationships
    if hasattr(model, 'entities'):
        for entity in model.entities:
            for prop in entity.properties:
                if prop.__class__.__name__ == 'Relationship':
                    if prop.type.name not in entity_names:
                        raise TextXSemanticError(f"Entity '{entity.name}' references unknown entity '{prop.type.name}' in relationship '{prop.name}'")

    # Additional cross-reference validations can be added here as needed


# Utility functions for getting model information

def get_class_name(obj):
    """Get the class name of an object"""
    return obj.__class__.__name__


def get_all_process_names(model):
    """Get all process names from the model"""
    return [process.name for process in model.processes] if hasattr(model, 'processes') else []


def get_all_entity_names(model):
    """Get all entity names from the model"""
    return [entity.name for entity in model.entities] if hasattr(model, 'entities') else []


def get_all_role_names(model):
    """Get all role names from the model"""
    return [role.name for role in model.roles] if hasattr(model, 'roles') else []


def get_process_elements(process):
    """Get all elements from a process"""
    return process.elements if hasattr(process, 'elements') else []


def get_process_flows(process):
    """Get all sequence flows from a process"""
    return process.flows if hasattr(process, 'flows') else []


def get_user_tasks(process):
    """Get all user tasks from a process"""
    return [elem for elem in get_process_elements(process)
            if elem.__class__.__name__ == 'UserTask']


def get_service_tasks(process):
    """Get all service tasks from a process"""
    return [elem for elem in get_process_elements(process)
            if elem.__class__.__name__ == 'ServiceTask']


def get_gateways(process):
    """Get all gateways from a process"""
    return [elem for elem in get_process_elements(process)
            if 'Gateway' in elem.__class__.__name__]


def get_events(process):
    """Get all events from a process"""
    return [elem for elem in get_process_elements(process)
            if 'Event' in elem.__class__.__name__]