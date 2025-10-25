"""
React frontend generator for BPML
Generates complete React application with process management and entity CRUD
"""

import os
from textx import generator
from textxjinja import textx_jinja_generator

from bpml.generator.util.filters import (
    format_type_typescript,
    is_enum_type,
    get_enum_values
)
from bpml.generator.util.file_util import (
    create_output_file,
    format_template_name
)
from bpml.generator.util.string_format_util import (
    capitalize_str,
    lower_first_str,
    snake_case,
    camel_case,
    upper_case,
    dash_case
)

__version__ = "0.1.0"
THIS_FOLDER = os.path.dirname(__file__)


@generator('bpml', 'react')
def bpml_generate_react(metamodel, model, output_path, overwrite, debug, **custom_args):
    """
    Generator for React frontend from BPML business process models

    Generates:
    - React project structure (package.json, etc.)
    - Entity CRUD components (List, Page, Dialog)
    - Process management components (Dashboard, TaskList, ProcessInstance)
    - Service layer for API communication
    - TypeScript type definitions
    - Routing and navigation
    """

    context = get_context(model)
    filters = get_filters()

    # Generate React project structure
    output_path = generate_react_structure(context, filters, output_path, overwrite)

    # Generate entity CRUD components
    generate_entity_components(context, filters, model, output_path, overwrite)

    # Generate entity services
    generate_entity_services(context, filters, model, output_path, overwrite)

    # Generate process management components
    generate_process_components(context, filters, model, output_path, overwrite)

    # Generate shared components
    generate_shared_components(context, filters, output_path, overwrite)


def generate_entity_components(context, filters, model, output_path, overwrite):
    """Generate CRUD components for each entity"""
    entity_template = os.path.join(THIS_FOLDER, 'template/entity_components')

    # Collect all entities from all processes
    all_entities = []
    for process in model.processes:
        if hasattr(process, 'elements') and process.elements:
            entities = [elem for elem in process.elements if elem.__class__.__name__ == 'Entity']
            all_entities.extend(entities)

    # Generate components for each entity
    for entity in all_entities:
        context['entity'] = entity
        context['entity_name'] = entity.name
        context['entity_name_cap'] = capitalize_str(entity.name)
        context['entity_name_lower'] = lower_first_str(entity.name)
        context['entity_name_dash'] = dash_case(entity.name)
        context['attributes'] = entity.attributes if hasattr(entity, 'attributes') else []

        # Run Jinja generator for entity components
        pages_folder = os.path.join(output_path, 'src/pages')
        textx_jinja_generator(entity_template, pages_folder, context, overwrite, filters=filters)


def generate_entity_services(context, filters, model, output_path, overwrite):
    """Generate service layer for each entity"""
    service_template = os.path.join(THIS_FOLDER, 'template/entity_services')

    # Collect all entities from all processes
    all_entities = []
    for process in model.processes:
        if hasattr(process, 'elements') and process.elements:
            entities = [elem for elem in process.elements if elem.__class__.__name__ == 'Entity']
            all_entities.extend(entities)

    # Generate service for each entity
    for entity in all_entities:
        context['entity'] = entity
        context['entity_name'] = entity.name
        context['entity_name_cap'] = capitalize_str(entity.name)
        context['entity_name_lower'] = lower_first_str(entity.name)
        context['entity_name_dash'] = dash_case(entity.name)
        context['attributes'] = entity.attributes if hasattr(entity, 'attributes') else []

        # Run Jinja generator for entity services
        services_folder = os.path.join(output_path, 'src/services')
        textx_jinja_generator(service_template, services_folder, context, overwrite, filters=filters)


def generate_process_components(context, filters, model, output_path, overwrite):
    """Generate process management components for each process"""
    process_template = os.path.join(THIS_FOLDER, 'template/process_components')

    # Generate components for each process
    for process in model.processes:
        # Extract process elements
        process_states = []
        process_roles = []
        process_steps = []
        process_transitions = []

        if hasattr(process, 'elements') and process.elements:
            for elem in process.elements:
                elem_type = elem.__class__.__name__
                if elem_type == 'State':
                    process_states.append(elem)
                elif elem_type == 'Role':
                    process_roles.append(elem)
                elif elem_type == 'Step':
                    process_steps.append(elem)
                elif elem_type == 'Transition':
                    process_transitions.append(elem)

        # Update context with process-specific data
        context['process'] = process
        context['process_name'] = process.name
        context['process_name_cap'] = capitalize_str(process.name)
        context['process_name_lower'] = lower_first_str(process.name)
        context['process_name_dash'] = dash_case(process.name)
        context['process_states'] = process_states
        context['process_roles'] = process_roles
        context['process_steps'] = process_steps
        context['process_transitions'] = process_transitions

        # Generate process components
        components_folder = os.path.join(output_path, 'src/components/processes')
        textx_jinja_generator(process_template, components_folder, context, overwrite, filters=filters)


def generate_shared_components(context, filters, output_path, overwrite):
    """Generate shared/reusable components"""
    shared_template = os.path.join(THIS_FOLDER, 'template/shared_components')
    shared_folder = os.path.join(output_path, 'src/components/shared')
    textx_jinja_generator(shared_template, shared_folder, context, overwrite, filters=filters)


def generate_react_structure(context, filters, output_path, overwrite):
    """Generate React project structure (package.json, public/, src/, etc.)"""
    react_structure_template = os.path.join(THIS_FOLDER, 'template/react_structure')
    output_path = create_output_file(output_path, 'generated_react')
    textx_jinja_generator(react_structure_template, output_path, context, overwrite, filters=filters)
    return output_path


def get_filters():
    """Return Jinja2 filters for template rendering"""
    return {
        'format_type': format_type_typescript,
        'is_enum_type': is_enum_type,
        'get_enum_values': get_enum_values,
        'format_template_name': format_template_name,
        'capitalize_str': capitalize_str,
        'lower_first_str': lower_first_str,
        'snake_case': snake_case,
        'camel_case': camel_case,
        'upper_case': upper_case,
        'dash_case': dash_case
    }


def get_context(model):
    """
    Prepare context dictionary for template rendering
    Extracts data from BPML model
    """
    project_name = model.project_info.projectName

    # Collect all entities from all processes
    all_entities = []
    all_entity_names = []
    for process in model.processes:
        if hasattr(process, 'elements') and process.elements:
            entities = [elem for elem in process.elements if elem.__class__.__name__ == 'Entity']
            all_entities.extend(entities)
            all_entity_names.extend([e.name for e in entities])

    context = {
        'app_name': project_name if project_name else 'BpmlApp',
        'app_name_lower': project_name.lower() if project_name else 'bpmlapp',
        'app_name_cap': capitalize_str(project_name) if project_name else 'BpmlApp',
        'app_name_dash': dash_case(project_name) if project_name else 'bpml-app',
        'project_info': model.project_info,
        'processes': model.processes,
        'entities': all_entities,
        'entity_names': all_entity_names
    }

    return context
