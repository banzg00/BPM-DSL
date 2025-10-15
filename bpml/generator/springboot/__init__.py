"""
Spring Boot backend generator for BPML
Generates clean Spring Boot project with CRUD operations for business process entities
"""

import os
from textx import generator
from textxjinja import textx_jinja_generator

from bpml.generator.util.filters import format_type_java, is_enum_type, get_enum_values
from bpml.generator.util.file_util import (
    create_output_file,
    get_main_java_folder_path,
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


@generator('bpml', 'springboot')
def bpml_generate_springboot(metamodel, model, output_path, overwrite, debug, **custom_args):
    """
    Generator for Spring Boot backend from BPML business process models

    Generates:
    - Spring Boot project structure (pom.xml, application.properties)
    - JPA entities for all process entities
    - Repositories with CRUD operations
    - Service layer with business logic
    - REST controllers with standard endpoints
    - DTOs and mappers
    - Exception handling
    """

    context = get_context(model)
    filters = get_filters()

    # Generate project structure
    output_path = generate_springboot_structure(context, filters, output_path, overwrite)

    # Generate main application class
    main_folder_path = generate_main_file(context, filters, output_path, overwrite)

    # Generate exception handling
    generate_exception_files(context, filters, main_folder_path, overwrite)

    # Generate config files
    generate_config_files(context, filters, main_folder_path, overwrite)

    # Generate CRUD for all entities from all processes
    generate_entity_files(context, filters, main_folder_path, model, overwrite)

    # Generate process runtime support (ProcessInstance, Tasks, etc.)
    generate_process_runtime_files(context, filters, main_folder_path, model, overwrite)


def generate_entity_files(context, filters, main_folder_path, model, overwrite):
    """Generate entity, repository, service, controller, DTO and mapper for each entity"""
    content_structure_template = os.path.join(THIS_FOLDER, 'template/content_structure')

    # Collect all Entity elements from all processes
    all_entities = []
    for process in model.processes:
        if hasattr(process, 'elements') and process.elements:
            # Filter only Entity type from elements (not Role, State, Transition, Step, Flow)
            entities = [elem for elem in process.elements if elem.__class__.__name__ == 'Entity']
            all_entities.extend(entities)

    # Generate CRUD for each entity
    for entity in all_entities:
        context['entity'] = entity
        context['entity_name'] = entity.name
        context['entity_name_cap'] = capitalize_str(entity.name)
        context['attributes'] = entity.attributes if hasattr(entity, 'attributes') else []

        # Generate enum types for entity attributes
        for attribute in context['attributes']:
            if is_enum_type(attribute.type):
                context['attribute_name_cap'] = capitalize_str(attribute.name)
                context['enum_values'] = get_enum_values(attribute.type)

                # Generate enum file
                enum_template = os.path.join(THIS_FOLDER, 'template/content_structure/model/enums')
                textx_jinja_generator(enum_template, main_folder_path, context, overwrite, filters=filters)

        # Run Jinja generator for entity files
        textx_jinja_generator(content_structure_template, main_folder_path, context, overwrite, filters=filters)


def generate_config_files(context, filters, main_folder_path, overwrite):
    """Generate configuration files (CORS, etc.)"""
    config_template = os.path.join(THIS_FOLDER, 'template/config_files')
    textx_jinja_generator(config_template, main_folder_path, context, overwrite, filters=filters)


def generate_process_runtime_files(context, filters, main_folder_path, model, overwrite):
    """Generate process runtime support (ProcessInstance, ProcessTask) for each process"""
    process_runtime_template = os.path.join(THIS_FOLDER, 'template/process_runtime')

    # Generate runtime support for each process
    for process in model.processes:
        # Extract states from process elements
        process_states = []
        process_roles = []
        process_steps = []

        if hasattr(process, 'elements') and process.elements:
            for elem in process.elements:
                elem_type = elem.__class__.__name__
                if elem_type == 'State':
                    process_states.append(elem)
                elif elem_type == 'Role':
                    process_roles.append(elem)
                elif elem_type == 'Step':
                    process_steps.append(elem)

        # Update context with process-specific data
        context['process_name'] = process.name
        context['process_states'] = process_states
        context['process_roles'] = process_roles
        context['process_steps'] = process_steps

        # Run Jinja generator
        textx_jinja_generator(process_runtime_template, main_folder_path, context, overwrite, filters=filters)


def generate_exception_files(context, filters, main_folder_path, overwrite):
    """Generate exception classes and global exception handler"""
    exception_template = os.path.join(THIS_FOLDER, 'template/exception_files')
    textx_jinja_generator(exception_template, main_folder_path, context, overwrite, filters=filters)


def generate_main_file(context, filters, output_path, overwrite):
    """Generate Spring Boot main application class"""
    main_file_template = os.path.join(THIS_FOLDER, 'template/main_file')
    main_folder_path = get_main_java_folder_path(output_path, context)
    textx_jinja_generator(main_file_template, main_folder_path, context, overwrite, filters=filters)
    return main_folder_path


def generate_springboot_structure(context, filters, output_path, overwrite):
    """Generate Spring Boot project structure (pom.xml, application.properties, etc.)"""
    springboot_structure_template = os.path.join(THIS_FOLDER, 'template/springboot_structure')
    output_path = create_output_file(output_path, 'generated_springboot')
    textx_jinja_generator(springboot_structure_template, output_path, context, overwrite, filters=filters)
    return output_path


def get_filters():
    """Return Jinja2 filters for template rendering"""
    return {
        'format_type_java': format_type_java,
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

    # Collect all Entity elements from all processes
    all_entities = []
    all_entity_names = []
    for process in model.processes:
        if hasattr(process, 'elements') and process.elements:
            # Filter only Entity type from elements
            entities = [elem for elem in process.elements if elem.__class__.__name__ == 'Entity']
            all_entities.extend(entities)
            all_entity_names.extend([e.name.lower() for e in entities])

    context = {
        'group_name': 'com.bpml',  # Default group name
        'app_name': project_name if project_name else 'BpmlApp',
        'app_name_lower': project_name.lower() if project_name else 'bpmlapp',
        'app_name_cap': capitalize_str(project_name) if project_name else 'BpmlApp',
        'project_info': model.project_info,
        'processes': model.processes,
        'entities': all_entities,
        'entity_names': all_entity_names
    }

    return context
