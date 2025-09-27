"""
Custom model classes for BPML (Business Process Modeling Language)
These classes extend the basic TextX generated model with additional functionality
"""

from textx import get_model_from_str
from typing import List, Dict, Set, Optional, Any
import uuid
from datetime import datetime, timedelta
from enum import Enum


class ProcessInstanceStatus(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    ERROR = "ERROR"


class TaskInstanceStatus(Enum):
    CREATED = "CREATED"
    READY = "READY"
    RESERVED = "RESERVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class SimpleType:
    """Enhanced SimpleType with validation capabilities"""

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __str__(self):
        return self.name

    def validate_value(self, value):
        """Validate a value against this type"""
        type_validators = {
            'int': lambda v: isinstance(v, int),
            'str': lambda v: isinstance(v, str),
            'float': lambda v: isinstance(v, (int, float)),
            'bool': lambda v: isinstance(v, bool),
            'long': lambda v: isinstance(v, int),
            'dateTime': lambda v: self._validate_datetime(v),
            'date': lambda v: self._validate_date(v),
            'decimal': lambda v: isinstance(v, (int, float)),
            'email': lambda v: self._validate_email(v),
            'phone': lambda v: self._validate_phone(v),
            'url': lambda v: self._validate_url(v)
        }

        validator = type_validators.get(self.name)
        return validator(value) if validator else True

    def _validate_datetime(self, value):
        """Validate datetime format"""
        try:
            datetime.fromisoformat(str(value))
            return True
        except:
            return False

    def _validate_date(self, value):
        """Validate date format"""
        try:
            datetime.strptime(str(value), '%Y-%m-%d')
            return True
        except:
            return False

    def _validate_email(self, value):
        """Basic email validation"""
        return isinstance(value, str) and '@' in value and '.' in value

    def _validate_phone(self, value):
        """Basic phone validation"""
        return isinstance(value, str) and len(value.replace('+', '').replace('-', '').replace(' ', '')) >= 10

    def _validate_url(self, value):
        """Basic URL validation"""
        return isinstance(value, str) and (value.startswith('http://') or value.startswith('https://'))


class ProcessInstance:
    """Represents a running instance of a business process"""

    def __init__(self, process_definition, initiator=None, process_data=None):
        self.id = str(uuid.uuid4())
        self.process_definition = process_definition
        self.status = ProcessInstanceStatus.CREATED
        self.initiator = initiator
        self.start_time = datetime.now()
        self.end_time = None
        self.current_elements = []
        self.completed_elements = []
        self.process_data = process_data or {}
        self.task_instances = []
        self.variables = {}

    def start(self):
        """Start the process instance"""
        self.status = ProcessInstanceStatus.RUNNING
        start_events = [elem for elem in self.process_definition.elements
                       if elem.__class__.__name__ == 'StartEvent']
        if start_events:
            self.current_elements = [start_events[0]]
            self._evaluate_start_event(start_events[0])

    def complete_task(self, task_id, form_data=None):
        """Complete a task instance"""
        task_instance = next((t for t in self.task_instances if t.id == task_id), None)
        if task_instance and task_instance.status == TaskInstanceStatus.IN_PROGRESS:
            task_instance.complete(form_data)
            self._advance_process(task_instance.task_definition)

    def _evaluate_start_event(self, start_event):
        """Evaluate start event and move to next elements"""
        if start_event.data:
            self._load_process_data(start_event.data)
        self._advance_process(start_event)

    def _advance_process(self, completed_element):
        """Advance process after completing an element"""
        self.completed_elements.append(completed_element)
        if completed_element in self.current_elements:
            self.current_elements.remove(completed_element)

        # Find next elements based on sequence flows
        next_elements = self._get_next_elements(completed_element)

        for next_element in next_elements:
            self._execute_element(next_element)

    def _execute_element(self, element):
        """Execute a process element"""
        element_type = element.__class__.__name__

        if element_type == 'UserTask':
            self._create_task_instance(element)
        elif element_type == 'ServiceTask':
            self._execute_service_task(element)
        elif element_type == 'ScriptTask':
            self._execute_script_task(element)
        elif element_type == 'ExclusiveGateway':
            self._evaluate_exclusive_gateway(element)
        elif element_type == 'ParallelGateway':
            self._evaluate_parallel_gateway(element)
        elif element_type == 'EndEvent':
            self._handle_end_event(element)

        if element not in self.current_elements:
            self.current_elements.append(element)

    def _create_task_instance(self, user_task):
        """Create a new task instance for a user task"""
        task_instance = TaskInstance(user_task, self)
        self.task_instances.append(task_instance)
        return task_instance

    def _execute_service_task(self, service_task):
        """Execute a service task"""
        # Simulate service task execution
        # In real implementation, this would call the actual service
        self._advance_process(service_task)

    def _execute_script_task(self, script_task):
        """Execute a script task"""
        # Simulate script execution
        # In real implementation, this would execute the script
        self._advance_process(script_task)

    def _evaluate_exclusive_gateway(self, gateway):
        """Evaluate exclusive gateway conditions"""
        for condition in gateway.conditions:
            if self._evaluate_condition(condition.condition):
                self._advance_process(gateway)
                self._execute_element(condition.target)
                return

        # Use default flow if no condition matches
        if hasattr(gateway, 'defaultFlow') and gateway.defaultFlow:
            self._execute_element(gateway.defaultFlow)

    def _evaluate_parallel_gateway(self, gateway):
        """Handle parallel gateway"""
        # For simplicity, immediately advance to all outgoing flows
        self._advance_process(gateway)

    def _handle_end_event(self, end_event):
        """Handle end event"""
        self.status = ProcessInstanceStatus.COMPLETED
        self.end_time = datetime.now()

        if hasattr(end_event, 'actions') and end_event.actions:
            for action in end_event.actions:
                self._execute_action(action)

    def _get_next_elements(self, element):
        """Get next elements in the process flow"""
        # This would be implemented based on sequence flows
        # For now, return empty list
        return []

    def _evaluate_condition(self, condition_string):
        """Evaluate a condition string"""
        # Simple condition evaluation
        # In real implementation, this would use a proper expression evaluator
        return True

    def _execute_action(self, action):
        """Execute an action"""
        # Implementation would depend on action type
        pass

    def _load_process_data(self, data_binding):
        """Load initial process data"""
        # Implementation would extract data based on binding type
        pass


class TaskInstance:
    """Represents an instance of a user task"""

    def __init__(self, task_definition, process_instance):
        self.id = str(uuid.uuid4())
        self.task_definition = task_definition
        self.process_instance = process_instance
        self.status = TaskInstanceStatus.CREATED
        self.assignee = None
        self.candidate_groups = []
        self.created_time = datetime.now()
        self.due_date = None
        self.completed_time = None
        self.form_data = {}

        self._initialize_task()

    def _initialize_task(self):
        """Initialize task with assignee and due date"""
        if self.task_definition.assignee:
            self.assignee = self._resolve_assignee(self.task_definition.assignee)

        if hasattr(self.task_definition, 'candidateGroups') and self.task_definition.candidateGroups:
            self.candidate_groups = [group.name for group in self.task_definition.candidateGroups]

        if hasattr(self.task_definition, 'dueDate') and self.task_definition.dueDate:
            self.due_date = self._parse_due_date(self.task_definition.dueDate)

        self.status = TaskInstanceStatus.READY

    def claim(self, user_id):
        """Claim the task for a specific user"""
        if self.status == TaskInstanceStatus.READY:
            self.assignee = user_id
            self.status = TaskInstanceStatus.RESERVED

    def start(self):
        """Start working on the task"""
        if self.status == TaskInstanceStatus.RESERVED:
            self.status = TaskInstanceStatus.IN_PROGRESS

    def complete(self, form_data=None):
        """Complete the task"""
        if self.status == TaskInstanceStatus.IN_PROGRESS:
            self.form_data = form_data or {}
            self.status = TaskInstanceStatus.COMPLETED
            self.completed_time = datetime.now()

            # Validate form data if form is defined
            if self.task_definition.form:
                self._validate_form_data()

            # Execute completion actions
            if hasattr(self.task_definition, 'completionActions') and self.task_definition.completionActions:
                self._execute_completion_actions()

    def delegate(self, new_assignee):
        """Delegate the task to another user"""
        self.assignee = new_assignee
        self.status = TaskInstanceStatus.READY

    def _resolve_assignee(self, assignee_definition):
        """Resolve assignee from definition"""
        assignee_type = assignee_definition.__class__.__name__

        if assignee_type == 'RoleAssignee':
            return f"role:{assignee_definition.role.name}"
        elif assignee_type == 'UserAssignee':
            return assignee_definition.username
        elif assignee_type == 'ExpressionAssignee':
            # Evaluate expression to get actual assignee
            return self._evaluate_assignee_expression(assignee_definition.expression)

        return None

    def _parse_due_date(self, due_date_string):
        """Parse due date string"""
        # Simple implementation - in practice would support various formats
        try:
            return datetime.fromisoformat(due_date_string)
        except:
            # Could support relative dates like "+3d", "+1w", etc.
            return datetime.now() + timedelta(days=1)

    def _validate_form_data(self):
        """Validate submitted form data"""
        form = self.task_definition.form

        for field in form.fields:
            field_name = field.name
            field_type = field.fieldType

            if field.required and field_name not in self.form_data:
                raise ValueError(f"Required field '{field_name}' is missing")

            if field_name in self.form_data:
                value = self.form_data[field_name]
                if not self._validate_field_value(value, field_type):
                    raise ValueError(f"Invalid value for field '{field_name}'")

    def _validate_field_value(self, value, field_type):
        """Validate a field value against its type"""
        type_validators = {
            'text': lambda v: isinstance(v, str),
            'number': lambda v: isinstance(v, (int, float)),
            'email': lambda v: isinstance(v, str) and '@' in v,
            'bool': lambda v: isinstance(v, bool),
            'date': lambda v: self._validate_date_string(v),
            'datetime': lambda v: self._validate_datetime_string(v)
        }

        validator = type_validators.get(field_type)
        return validator(value) if validator else True

    def _validate_date_string(self, value):
        """Validate date string"""
        try:
            datetime.strptime(str(value), '%Y-%m-%d')
            return True
        except:
            return False

    def _validate_datetime_string(self, value):
        """Validate datetime string"""
        try:
            datetime.fromisoformat(str(value))
            return True
        except:
            return False

    def _execute_completion_actions(self):
        """Execute actions defined for task completion"""
        # Implementation would handle different types of completion actions
        pass

    def _evaluate_assignee_expression(self, expression):
        """Evaluate assignee expression"""
        # Simple expression evaluation - in practice would use proper parser
        return "system"


class FormFieldDefinition:
    """Enhanced form field with validation and rendering info"""

    def __init__(self, parent, name, fieldType, readonly=False, required=False):
        self.parent = parent
        self.name = name
        self.fieldType = fieldType
        self.readonly = readonly
        self.required = required
        self.validation_rules = []
        self.options = []  # For select/radio fields
        self.placeholder = None
        self.help_text = None

    def add_validation_rule(self, rule_type, parameters):
        """Add validation rule to field"""
        self.validation_rules.append({
            'type': rule_type,
            'parameters': parameters
        })

    def validate_value(self, value):
        """Validate field value against all rules"""
        if self.required and (value is None or value == ''):
            return False, "Field is required"

        for rule in self.validation_rules:
            is_valid, message = self._apply_validation_rule(value, rule)
            if not is_valid:
                return False, message

        return True, None

    def _apply_validation_rule(self, value, rule):
        """Apply a specific validation rule"""
        rule_type = rule['type']
        params = rule['parameters']

        if rule_type == 'minLength' and len(str(value)) < int(params):
            return False, f"Minimum length is {params}"
        elif rule_type == 'maxLength' and len(str(value)) > int(params):
            return False, f"Maximum length is {params}"
        elif rule_type == 'pattern':
            import re
            if not re.match(params, str(value)):
                return False, "Value doesn't match required pattern"

        return True, None


class ProcessAnalyzer:
    """Utility class for analyzing process definitions"""

    def __init__(self, process_definition):
        self.process = process_definition
        self.element_graph = self._build_element_graph()

    def _build_element_graph(self):
        """Build a graph of process elements and their connections"""
        graph = {}

        # Initialize graph with all elements
        for element in self.process.elements:
            element_id = self._get_element_id(element)
            graph[element_id] = {
                'element': element,
                'incoming': [],
                'outgoing': []
            }

        # Add connections based on sequence flows
        if hasattr(self.process, 'flows') and self.process.flows:
            for flow in self.process.flows:
                source_id = self._get_element_id(flow.source)
                target_id = self._get_element_id(flow.target)

                if source_id in graph and target_id in graph:
                    graph[source_id]['outgoing'].append(target_id)
                    graph[target_id]['incoming'].append(source_id)

        return graph

    def _get_element_id(self, element):
        """Get unique identifier for an element"""
        return element.name if hasattr(element, 'name') else str(element)

    def find_cycles(self):
        """Find cycles in the process flow"""
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.element_graph.get(node, {}).get('outgoing', []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    cycles.append(f"Cycle detected: {node} -> {neighbor}")
                    return True

            rec_stack.remove(node)
            return False

        for node in self.element_graph:
            if node not in visited:
                dfs(node)

        return cycles

    def find_orphaned_elements(self):
        """Find elements with no incoming or outgoing connections"""
        orphaned = []

        for element_id, info in self.element_graph.items():
            element = info['element']
            element_type = element.__class__.__name__

            # Start events should have no incoming connections
            if element_type != 'StartEvent' and not info['incoming']:
                orphaned.append(f"Element '{element_id}' has no incoming connections")

            # End events should have no outgoing connections
            if element_type != 'EndEvent' and not info['outgoing']:
                orphaned.append(f"Element '{element_id}' has no outgoing connections")

        return orphaned

    def validate_gateway_conditions(self):
        """Validate gateway conditions"""
        issues = []

        for element in self.process.elements:
            if element.__class__.__name__ in ['ExclusiveGateway', 'InclusiveGateway']:
                if not hasattr(element, 'conditions') or not element.conditions:
                    issues.append(f"Gateway '{element.name}' has no conditions defined")

                # Check for overlapping conditions (simplified)
                if hasattr(element, 'conditions'):
                    conditions = [c.condition for c in element.conditions]
                    if len(conditions) != len(set(conditions)):
                        issues.append(f"Gateway '{element.name}' has duplicate conditions")

        return issues

    def get_process_paths(self):
        """Get all possible execution paths through the process"""
        start_events = [elem for elem in self.process.elements
                       if elem.__class__.__name__ == 'StartEvent']
        end_events = [elem for elem in self.process.elements
                     if elem.__class__.__name__ == 'EndEvent']

        paths = []

        for start in start_events:
            for end in end_events:
                path = self._find_path(start, end)
                if path:
                    paths.append(path)

        return paths

    def _find_path(self, start_element, end_element):
        """Find path between two elements using DFS"""
        start_id = self._get_element_id(start_element)
        end_id = self._get_element_id(end_element)

        visited = set()
        path = []

        def dfs(current_id):
            if current_id == end_id:
                path.append(current_id)
                return True

            if current_id in visited:
                return False

            visited.add(current_id)
            path.append(current_id)

            for neighbor in self.element_graph.get(current_id, {}).get('outgoing', []):
                if dfs(neighbor):
                    return True

            path.pop()
            return False

        if dfs(start_id):
            return path

        return None