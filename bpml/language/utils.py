"""
Utility functions for BPML (Business Process Modeling Language)
These functions provide helper methods for process analysis, transformation, and code generation support
"""

from typing import List, Dict, Set, Tuple, Any, Optional
from collections import defaultdict, deque
import json
import re
from datetime import datetime, timedelta


class ProcessAnalyzer:
    """
    Comprehensive analyzer for business process models
    Provides methods for process validation, optimization, and analysis
    """

    def __init__(self, process_model):
        self.process_model = process_model
        self.element_graph = self._build_element_graph()
        self.flow_graph = self._build_flow_graph()

    def _build_element_graph(self):
        """Build a graph of process elements and their relationships"""
        graph = {}

        if not hasattr(self.process_model, 'elements'):
            return graph

        for element in self.process_model.elements:
            element_id = element.name
            graph[element_id] = {
                'element': element,
                'type': element.__class__.__name__,
                'incoming': [],
                'outgoing': [],
                'properties': self._extract_element_properties(element)
            }

        return graph

    def _build_flow_graph(self):
        """Build a graph based on sequence flows"""
        if not hasattr(self.process_model, 'flows') or not self.process_model.flows:
            return {}

        flow_graph = defaultdict(list)

        for flow in self.process_model.flows:
            source_name = flow.source.name
            target_name = flow.target.name

            flow_graph[source_name].append({
                'target': target_name,
                'condition': getattr(flow, 'condition', None),
                'name': getattr(flow, 'name', None)
            })

            # Update element graph with flow information
            if source_name in self.element_graph:
                self.element_graph[source_name]['outgoing'].append(target_name)
            if target_name in self.element_graph:
                self.element_graph[target_name]['incoming'].append(source_name)

        return dict(flow_graph)

    def _extract_element_properties(self, element):
        """Extract relevant properties from a process element"""
        properties = {
            'name': element.name,
            'type': element.__class__.__name__
        }

        # Extract type-specific properties
        if hasattr(element, 'assignee') and element.assignee:
            properties['assignee'] = self._serialize_assignee(element.assignee)

        if hasattr(element, 'candidateGroups') and element.candidateGroups:
            properties['candidateGroups'] = [group.name for group in element.candidateGroups]

        if hasattr(element, 'form') and element.form:
            properties['hasForm'] = True
            properties['formFields'] = [field.name for field in element.form.fields]

        if hasattr(element, 'implementation') and element.implementation:
            properties['implementation'] = element.implementation

        if hasattr(element, 'conditions') and element.conditions:
            properties['conditions'] = [cond.condition for cond in element.conditions]

        return properties

    def _serialize_assignee(self, assignee):
        """Serialize assignee information"""
        assignee_type = assignee.__class__.__name__

        if assignee_type == 'RoleAssignee':
            return {'type': 'role', 'value': assignee.role.name}
        elif assignee_type == 'UserAssignee':
            return {'type': 'user', 'value': assignee.username}
        elif assignee_type == 'ExpressionAssignee':
            return {'type': 'expression', 'value': assignee.expression}

        return {'type': 'unknown', 'value': str(assignee)}

    def find_execution_paths(self):
        """Find all possible execution paths through the process"""
        start_elements = [name for name, info in self.element_graph.items()
                         if info['type'] == 'StartEvent']
        end_elements = [name for name, info in self.element_graph.items()
                       if info['type'] == 'EndEvent']

        all_paths = []

        for start in start_elements:
            for end in end_elements:
                paths = self._find_paths_between(start, end)
                all_paths.extend(paths)

        return all_paths

    def _find_paths_between(self, start, end, max_depth=50):
        """Find all paths between two elements using DFS with depth limit"""
        paths = []
        visited = set()

        def dfs(current, path, depth):
            if depth > max_depth:
                return

            if current == end:
                paths.append(path + [current])
                return

            if current in visited:
                return

            visited.add(current)

            for neighbor in self.element_graph.get(current, {}).get('outgoing', []):
                dfs(neighbor, path + [current], depth + 1)

            visited.remove(current)

        dfs(start, [], 0)
        return paths

    def detect_cycles(self):
        """Detect cycles in the process flow"""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.element_graph.get(node, {}).get('outgoing', []):
                if neighbor not in visited:
                    cycle_path = dfs(neighbor, path + [node])
                    if cycle_path:
                        cycles.append(cycle_path)
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor) if neighbor in path else 0
                    cycles.append(path[cycle_start:] + [node, neighbor])

            rec_stack.remove(node)
            return None

        for node in self.element_graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def find_orphaned_elements(self):
        """Find elements that are not properly connected"""
        orphaned = []

        for element_name, info in self.element_graph.items():
            element_type = info['type']

            # Start events should have no incoming connections
            if element_type == 'StartEvent' and info['incoming']:
                orphaned.append({
                    'element': element_name,
                    'type': element_type,
                    'issue': 'Start event has incoming connections'
                })

            # End events should have no outgoing connections
            elif element_type == 'EndEvent' and info['outgoing']:
                orphaned.append({
                    'element': element_name,
                    'type': element_type,
                    'issue': 'End event has outgoing connections'
                })

            # Other elements should have both incoming and outgoing
            elif element_type not in ['StartEvent', 'EndEvent']:
                if not info['incoming']:
                    orphaned.append({
                        'element': element_name,
                        'type': element_type,
                        'issue': 'No incoming connections'
                    })
                if not info['outgoing']:
                    orphaned.append({
                        'element': element_name,
                        'type': element_type,
                        'issue': 'No outgoing connections'
                    })

        return orphaned

    def calculate_process_metrics(self):
        """Calculate various process metrics"""
        metrics = {
            'total_elements': len(self.element_graph),
            'start_events': len([e for e in self.element_graph.values() if e['type'] == 'StartEvent']),
            'end_events': len([e for e in self.element_graph.values() if e['type'] == 'EndEvent']),
            'user_tasks': len([e for e in self.element_graph.values() if e['type'] == 'UserTask']),
            'service_tasks': len([e for e in self.element_graph.values() if e['type'] == 'ServiceTask']),
            'gateways': len([e for e in self.element_graph.values() if 'Gateway' in e['type']]),
            'parallel_paths': self._count_parallel_paths(),
            'max_path_length': self._calculate_max_path_length(),
            'avg_path_length': self._calculate_avg_path_length(),
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity()
        }

        return metrics

    def _count_parallel_paths(self):
        """Count the maximum number of parallel execution paths"""
        parallel_gateways = [name for name, info in self.element_graph.items()
                           if info['type'] == 'ParallelGateway']

        max_parallel = 1
        for gateway in parallel_gateways:
            outgoing_count = len(self.element_graph[gateway]['outgoing'])
            max_parallel = max(max_parallel, outgoing_count)

        return max_parallel

    def _calculate_max_path_length(self):
        """Calculate the maximum path length in the process"""
        all_paths = self.find_execution_paths()
        return max([len(path) for path in all_paths]) if all_paths else 0

    def _calculate_avg_path_length(self):
        """Calculate the average path length in the process"""
        all_paths = self.find_execution_paths()
        if not all_paths:
            return 0
        return sum([len(path) for path in all_paths]) / len(all_paths)

    def _calculate_cyclomatic_complexity(self):
        """Calculate McCabe's cyclomatic complexity for the process"""
        # Simplified calculation: number of decision points + 1
        decision_points = len([e for e in self.element_graph.values()
                             if e['type'] in ['ExclusiveGateway', 'InclusiveGateway']])
        return decision_points + 1

    def find_bottlenecks(self):
        """Identify potential bottlenecks in the process"""
        bottlenecks = []

        for element_name, info in self.element_graph.items():
            element_type = info['type']

            # Elements with many incoming flows might be bottlenecks
            if len(info['incoming']) > 2:
                bottlenecks.append({
                    'element': element_name,
                    'type': element_type,
                    'reason': f'High fan-in: {len(info["incoming"])} incoming flows',
                    'severity': 'medium'
                })

            # User tasks without candidate groups might create bottlenecks
            if element_type == 'UserTask':
                properties = info['properties']
                if 'candidateGroups' not in properties and 'assignee' in properties:
                    assignee = properties['assignee']
                    if assignee['type'] == 'user':
                        bottlenecks.append({
                            'element': element_name,
                            'type': element_type,
                            'reason': 'Single user assignment without candidate groups',
                            'severity': 'high'
                        })

        return bottlenecks

    def suggest_optimizations(self):
        """Suggest process optimizations"""
        suggestions = []

        # Analyze for parallel opportunities
        sequential_tasks = self._find_sequential_user_tasks()
        if len(sequential_tasks) > 1:
            suggestions.append({
                'type': 'parallelization',
                'description': f'Consider parallelizing tasks: {", ".join(sequential_tasks)}',
                'elements': sequential_tasks,
                'priority': 'medium'
            })

        # Check for redundant gateways
        redundant_gateways = self._find_redundant_gateways()
        for gateway in redundant_gateways:
            suggestions.append({
                'type': 'simplification',
                'description': f'Gateway "{gateway}" might be redundant',
                'elements': [gateway],
                'priority': 'low'
            })

        # Check for missing error handling
        service_tasks_without_error_handling = self._find_service_tasks_without_error_handling()
        for task in service_tasks_without_error_handling:
            suggestions.append({
                'type': 'error_handling',
                'description': f'Add error handling to service task "{task}"',
                'elements': [task],
                'priority': 'high'
            })

        return suggestions

    def _find_sequential_user_tasks(self):
        """Find user tasks that are executed sequentially and might be parallelized"""
        sequential_tasks = []

        for element_name, info in self.element_graph.items():
            if info['type'] == 'UserTask':
                outgoing = info['outgoing']
                if len(outgoing) == 1:
                    next_element = outgoing[0]
                    next_info = self.element_graph.get(next_element, {})
                    if next_info.get('type') == 'UserTask':
                        sequential_tasks.extend([element_name, next_element])

        return list(set(sequential_tasks))

    def _find_redundant_gateways(self):
        """Find gateways that might be redundant"""
        redundant = []

        for element_name, info in self.element_graph.items():
            if 'Gateway' in info['type']:
                incoming = info['incoming']
                outgoing = info['outgoing']

                # Gateway with only one incoming and one outgoing might be redundant
                if len(incoming) == 1 and len(outgoing) == 1:
                    redundant.append(element_name)

        return redundant

    def _find_service_tasks_without_error_handling(self):
        """Find service tasks that don't have error handling"""
        tasks_without_error_handling = []

        for element_name, info in self.element_graph.items():
            if info['type'] == 'ServiceTask':
                element = info['element']
                # Check if service task has error handling defined
                has_error_handling = (
                    hasattr(element, 'onFailure') and element.onFailure or
                    hasattr(element, 'retryCount') and element.retryCount and element.retryCount > 0
                )

                if not has_error_handling:
                    tasks_without_error_handling.append(element_name)

        return tasks_without_error_handling


class EntityExtractor:
    """
    Utility class for extracting and analyzing entity relationships in BPML models
    """

    def __init__(self, bpml_model):
        self.model = bpml_model
        self.entities = getattr(bpml_model, 'entities', [])
        self.processes = getattr(bpml_model, 'processes', [])

    def extract_entity_dependencies(self):
        """Extract dependencies between entities"""
        dependencies = defaultdict(set)

        for entity in self.entities:
            for prop in entity.properties:
                if prop.__class__.__name__ == 'Relationship':
                    target_entity = prop.type.name
                    dependencies[entity.name].add(target_entity)

        return dict(dependencies)

    def find_entity_usage_in_processes(self):
        """Find where entities are used in processes"""
        usage = defaultdict(list)

        for process in self.processes:
            # Check data objects
            if hasattr(process, 'elements'):
                for element in process.elements:
                    if element.__class__.__name__ == 'DataObject':
                        if hasattr(element, 'dataType') and element.dataType:
                            entity_name = self._extract_entity_name_from_data_type(element.dataType)
                            if entity_name:
                                usage[entity_name].append({
                                    'process': process.name,
                                    'element': element.name,
                                    'type': 'data_object'
                                })

            # Check form fields that reference entities
            user_tasks = [elem for elem in process.elements
                         if elem.__class__.__name__ == 'UserTask']

            for task in user_tasks:
                if hasattr(task, 'form') and task.form:
                    for field in task.form.fields:
                        if field.fieldType == 'entity':
                            # This would need to be extended based on how entity fields are defined
                            pass

        return dict(usage)

    def _extract_entity_name_from_data_type(self, data_type):
        """Extract entity name from data type definition"""
        if data_type.__class__.__name__ == 'EntityType':
            return data_type.entity.name
        elif data_type.__class__.__name__ == 'ListType':
            return self._extract_entity_name_from_data_type(data_type.elementType)
        return None

    def generate_entity_relationship_diagram(self):
        """Generate data for entity relationship diagram"""
        entities_data = []
        relationships_data = []

        for entity in self.entities:
            # Extract entity attributes
            attributes = []
            for prop in entity.properties:
                if prop.__class__.__name__ == 'Attribute':
                    attributes.append({
                        'name': prop.name,
                        'type': prop.type.name,
                        'isList': getattr(prop, 'isList', False),
                        'isOptional': getattr(prop, 'isOptional', False)
                    })

            entities_data.append({
                'name': entity.name,
                'attributes': attributes
            })

            # Extract relationships
            for prop in entity.properties:
                if prop.__class__.__name__ == 'Relationship':
                    relationships_data.append({
                        'source': entity.name,
                        'target': prop.type.name,
                        'name': prop.name,
                        'cardinality': prop.cardinality,
                        'isOptional': getattr(prop, 'isOptional', False)
                    })

        return {
            'entities': entities_data,
            'relationships': relationships_data
        }


class FormGenerator:
    """
    Utility class for generating form definitions and validation
    """

    @staticmethod
    def generate_crud_forms_for_entity(entity):
        """Generate CRUD forms for an entity"""
        forms = {}

        # Create form
        create_fields = []
        for prop in entity.properties:
            if prop.__class__.__name__ == 'Attribute':
                field_type = FormGenerator._map_attribute_to_form_field(prop)
                create_fields.append({
                    'name': prop.name,
                    'type': field_type,
                    'required': not getattr(prop, 'isOptional', False),
                    'label': FormGenerator._generate_field_label(prop.name)
                })

        forms['create'] = {
            'name': f'Create{entity.name}Form',
            'title': f'Create {entity.name}',
            'fields': create_fields
        }

        # Update form (similar to create but might exclude certain fields)
        update_fields = [field.copy() for field in create_fields]
        forms['update'] = {
            'name': f'Update{entity.name}Form',
            'title': f'Update {entity.name}',
            'fields': update_fields
        }

        # View form (readonly version)
        view_fields = [dict(field, readonly=True) for field in create_fields]
        forms['view'] = {
            'name': f'View{entity.name}Form',
            'title': f'View {entity.name}',
            'fields': view_fields
        }

        return forms

    @staticmethod
    def _map_attribute_to_form_field(attribute):
        """Map entity attribute type to form field type"""
        type_mapping = {
            'str': 'text',
            'int': 'number',
            'float': 'number',
            'bool': 'checkbox',
            'date': 'date',
            'dateTime': 'datetime',
            'email': 'email',
            'phone': 'text',
            'url': 'text',
            'text': 'textarea'
        }

        attr_type = attribute.type.name
        return type_mapping.get(attr_type, 'text')

    @staticmethod
    def _generate_field_label(field_name):
        """Generate user-friendly label from field name"""
        # Convert camelCase to Title Case
        words = re.sub(r'([A-Z])', r' \1', field_name).strip().split()
        return ' '.join(word.capitalize() for word in words)


class RoleHierarchyAnalyzer:
    """
    Utility class for analyzing role hierarchies and permissions
    """

    def __init__(self, roles):
        self.roles = roles
        self.hierarchy = self._build_hierarchy()

    def _build_hierarchy(self):
        """Build role hierarchy tree"""
        hierarchy = {}

        for role in self.roles:
            hierarchy[role.name] = {
                'role': role,
                'parent': role.parent.name if hasattr(role, 'parent') and role.parent else None,
                'children': [],
                'permissions': getattr(role, 'permissions', [])
            }

        # Build parent-child relationships
        for role_name, role_info in hierarchy.items():
            parent_name = role_info['parent']
            if parent_name and parent_name in hierarchy:
                hierarchy[parent_name]['children'].append(role_name)

        return hierarchy

    def get_effective_permissions(self, role_name):
        """Get all effective permissions for a role (including inherited)"""
        if role_name not in self.hierarchy:
            return []

        permissions = set()
        current_role = self.hierarchy[role_name]

        # Add own permissions
        permissions.update(perm.name for perm in current_role['permissions'])

        # Add inherited permissions
        parent_name = current_role['parent']
        while parent_name and parent_name in self.hierarchy:
            parent_role = self.hierarchy[parent_name]
            permissions.update(perm.name for perm in parent_role['permissions'])
            parent_name = parent_role['parent']

        return list(permissions)

    def find_role_conflicts(self):
        """Find potential conflicts in role definitions"""
        conflicts = []

        # Check for circular inheritance
        for role_name in self.hierarchy:
            if self._has_circular_inheritance(role_name):
                conflicts.append({
                    'type': 'circular_inheritance',
                    'role': role_name,
                    'description': f'Role {role_name} has circular inheritance'
                })

        # Check for duplicate permissions in hierarchy
        for role_name, role_info in self.hierarchy.items():
            parent_permissions = set()
            parent_name = role_info['parent']

            if parent_name and parent_name in self.hierarchy:
                parent_permissions = set(perm.name for perm in
                                       self.hierarchy[parent_name]['permissions'])

            own_permissions = set(perm.name for perm in role_info['permissions'])
            duplicate_permissions = own_permissions.intersection(parent_permissions)

            if duplicate_permissions:
                conflicts.append({
                    'type': 'duplicate_permissions',
                    'role': role_name,
                    'permissions': list(duplicate_permissions),
                    'description': f'Role {role_name} has permissions already inherited from parent'
                })

        return conflicts

    def _has_circular_inheritance(self, role_name, visited=None):
        """Check if a role has circular inheritance"""
        if visited is None:
            visited = set()

        if role_name in visited:
            return True

        visited.add(role_name)

        role_info = self.hierarchy.get(role_name)
        if role_info and role_info['parent']:
            return self._has_circular_inheritance(role_info['parent'], visited)

        return False


def generate_process_documentation(process):
    """Generate documentation for a process"""
    doc = {
        'name': process.name,
        'description': getattr(process, 'description', ''),
        'version': getattr(process, 'version', '1.0'),
        'elements': [],
        'flows': [],
        'roles_involved': set(),
        'entities_used': set()
    }

    # Document elements
    if hasattr(process, 'elements'):
        for element in process.elements:
            element_doc = {
                'name': element.name,
                'type': element.__class__.__name__,
                'description': getattr(element, 'description', '')
            }

            # Add type-specific documentation
            if element.__class__.__name__ == 'UserTask':
                if hasattr(element, 'assignee') and element.assignee:
                    assignee_type = element.assignee.__class__.__name__
                    if assignee_type == 'RoleAssignee':
                        doc['roles_involved'].add(element.assignee.role.name)
                        element_doc['assignee'] = f"Role: {element.assignee.role.name}"

                if hasattr(element, 'candidateGroups') and element.candidateGroups:
                    groups = [group.name for group in element.candidateGroups]
                    doc['roles_involved'].update(groups)
                    element_doc['candidateGroups'] = groups

            elif element.__class__.__name__ == 'ServiceTask':
                element_doc['implementation'] = getattr(element, 'implementation', '')

            doc['elements'].append(element_doc)

    # Document flows
    if hasattr(process, 'flows'):
        for flow in process.flows:
            flow_doc = {
                'source': flow.source.name,
                'target': flow.target.name,
                'condition': getattr(flow, 'condition', None)
            }
            doc['flows'].append(flow_doc)

    # Convert sets to lists for JSON serialization
    doc['roles_involved'] = list(doc['roles_involved'])
    doc['entities_used'] = list(doc['entities_used'])

    return doc


def validate_process_completeness(process):
    """Validate that a process is complete and ready for execution"""
    issues = []

    # Check for start and end events
    elements = getattr(process, 'elements', [])
    start_events = [e for e in elements if e.__class__.__name__ == 'StartEvent']
    end_events = [e for e in elements if e.__class__.__name__ == 'EndEvent']

    if not start_events:
        issues.append("Process must have at least one start event")
    if not end_events:
        issues.append("Process must have at least one end event")

    # Check user tasks have assignees
    user_tasks = [e for e in elements if e.__class__.__name__ == 'UserTask']
    for task in user_tasks:
        if not hasattr(task, 'assignee') or not task.assignee:
            if not hasattr(task, 'candidateGroups') or not task.candidateGroups:
                issues.append(f"User task '{task.name}' has no assignee or candidate groups")

    # Check service tasks have implementations
    service_tasks = [e for e in elements if e.__class__.__name__ == 'ServiceTask']
    for task in service_tasks:
        if not hasattr(task, 'implementation') or not task.implementation:
            issues.append(f"Service task '{task.name}' has no implementation defined")

    # Check gateways have conditions
    gateways = [e for e in elements if 'Gateway' in e.__class__.__name__]
    for gateway in gateways:
        if gateway.__class__.__name__ in ['ExclusiveGateway', 'InclusiveGateway']:
            if not hasattr(gateway, 'conditions') or not gateway.conditions:
                issues.append(f"Gateway '{gateway.name}' has no conditions defined")

    return issues


def estimate_process_execution_time(process, task_estimates=None):
    """Estimate process execution time based on task estimates"""
    if task_estimates is None:
        task_estimates = {}

    analyzer = ProcessAnalyzer(process)
    paths = analyzer.find_execution_paths()

    if not paths:
        return 0

    # Calculate time for each path
    path_times = []

    for path in paths:
        path_time = 0

        for element_name in path:
            element_info = analyzer.element_graph.get(element_name, {})
            element_type = element_info.get('type', '')

            # Get estimated time for this element
            if element_name in task_estimates:
                element_time = task_estimates[element_name]
            else:
                # Default estimates by element type (in minutes)
                default_estimates = {
                    'UserTask': 30,
                    'ServiceTask': 2,
                    'ScriptTask': 1,
                    'StartEvent': 0,
                    'EndEvent': 0,
                    'ExclusiveGateway': 0,
                    'ParallelGateway': 0,
                    'InclusiveGateway': 0
                }
                element_time = default_estimates.get(element_type, 0)

            path_time += element_time

        path_times.append(path_time)

    # Return statistics
    return {
        'min_time': min(path_times),
        'max_time': max(path_times),
        'avg_time': sum(path_times) / len(path_times),
        'path_count': len(path_times)
    }