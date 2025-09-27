# BPML - Business Process Modeling Language

BPML is a comprehensive Domain-Specific Language (DSL) for defining business processes that can generate complete fullstack applications with CRUD operations, process management, and user interfaces.

## Overview

BPML enables users to declaratively define:
- **Business Processes**: Complete workflows with activities, gateways, and events
- **Data Models**: Entities and relationships for process data
- **User Interfaces**: Forms and dashboards for process interaction
- **Roles & Security**: User roles and permissions for process access
- **Process Analytics**: Monitoring and reporting capabilities

## Language Features

### Process Elements
- **Events**: Start, End, and Intermediate events with conditions and triggers
- **Activities**: User tasks, Service tasks, and Script tasks
- **Gateways**: Exclusive, Parallel, and Inclusive decision points
- **Data Objects**: Process variables and business entities
- **Sequence Flows**: Process flow control with conditions

### Advanced Features
- **Role-based Security**: Built-in authorization and user assignment
- **Form Generation**: Automatic UI generation for user tasks
- **Dashboard Creation**: Process monitoring and management interfaces
- **Error Handling**: Retry mechanisms and failure paths
- **Escalation**: Automatic task escalation and notifications

## Quick Start

### 1. Define a Simple Process

```bpml
project {
    name: "SimpleApproval"
    description: "Basic approval workflow"
}

role Requestor {
    permissions: [submit_request, view_status]
}

role Approver {
    permissions: [approve_request, reject_request]
}

entity ApprovalRequest {
    requestId: str
    title: str
    description: text
    amount: decimal
    status: str
}

process SimpleApprovalProcess {
    start RequestSubmitted {
        trigger: "request_created"
        data: ApprovalRequest request
    }

    userTask ReviewRequest {
        assignee: role(Approver)
        form: ApprovalForm {
            fields: {
                title: text readonly
                description: textarea readonly
                amount: number readonly
                decision: select required
                comments: textarea
            }
        }
        onComplete: {
            if (form.decision == "approve") -> RequestApproved
            else -> RequestRejected
        }
    }

    end RequestApproved {
        actions: {
            sendNotification(request.requestorEmail, "Request approved")
            updateEntity("ApprovalRequest", "status", "APPROVED")
        }
    }

    end RequestRejected {
        actions: {
            sendNotification(request.requestorEmail, "Request rejected")
            updateEntity("ApprovalRequest", "status", "REJECTED")
        }
    }
}
```

### 2. Using the BPML API

```python
from textx import metamodel_from_file
from bpml.processors import semantic_check
from bpml.custom_model import ProcessInstance

# Load BPML metamodel
metamodel = metamodel_from_file('bpml.tx')
metamodel.register_model_processor(semantic_check)

# Parse a BPML model
model = metamodel.model_from_file('simple_approval.bpml')

# Create and start process instance
process = model.processes[0]
instance = ProcessInstance(process, initiator="user123")
instance.start()

# Complete a task
task_id = instance.task_instances[0].id
instance.complete_task(task_id, {"decision": "approve", "comments": "Looks good!"})
```

## File Structure

```
bpml/
├── bpml.tx                    # TextX grammar definition
├── custom_model.py            # Enhanced model classes
├── processors.py              # Semantic validation
├── utils.py                   # Utility functions
├── __init__.py               # Package initialization
├── README.md                 # This file
└── examples/                 # Example processes
    ├── order_management.bpml      # E-commerce workflow
    ├── employee_onboarding.bpml   # HR onboarding process
    └── document_approval.bpml     # Document approval workflow
```

## Core Components

### 1. Grammar Definition (`bpml.tx`)
The TextX grammar that defines the BPML language syntax, including:
- Process definitions and elements
- Entity and relationship modeling
- Role and permission structures
- Form and dashboard specifications

### 2. Custom Models (`custom_model.py`)
Enhanced classes that extend basic TextX functionality:
- `ProcessInstance`: Runtime process execution
- `TaskInstance`: Individual task management
- `ProcessAnalyzer`: Process validation and optimization
- `FormFieldDefinition`: Enhanced form handling

### 3. Semantic Processors (`processors.py`)
Validation and semantic checking functions:
- Process structure validation
- Role and permission verification
- Entity relationship validation
- Form field type checking
- Cross-reference validation

### 4. Utility Functions (`utils.py`)
Helper functions for process analysis and generation:
- `ProcessAnalyzer`: Flow analysis and optimization
- `EntityExtractor`: Entity relationship mapping
- `FormGenerator`: Automatic form generation
- `RoleHierarchyAnalyzer`: Role and permission analysis

## Language Reference

### Project Definition
```bpml
project {
    name: "ProjectName"
    description: "Project description"
    version: "1.0"
    author: "Author name"
}
```

### Entity Definition
```bpml
entity EntityName {
    attribute1: str
    attribute2: int
    relationship1: OtherEntity @1..1
    optionalField: str?
    listField: str[]
}
```

### Role Definition
```bpml
role RoleName extends ParentRole {
    permissions: [permission1, permission2]
    description: "Role description"
}
```

### Process Definition
```bpml
process ProcessName {
    description: "Process description"

    start StartEventName {
        trigger: "event_trigger"
        data: EntityType dataVar
    }

    userTask TaskName {
        assignee: role(RoleName)
        form: FormName {
            fields: {
                field1: text required
                field2: number readonly
            }
        }
        onComplete: {
            if (condition) -> NextElement
            else -> AlternativeElement
        }
    }

    end EndEventName {
        actions: {
            sendNotification(recipient, message)
            updateEntity("EntityName", "field", "value")
        }
    }
}
```

### Dashboard Definition
```bpml
dashboard DashboardName {
    title: "Dashboard Title"

    widgets: {
        taskList: {
            title: "My Tasks"
            filter: "assignee == currentUser"
            actions: [complete, delegate]
        }

        chart: ChartName {
            type: bar
            title: "Chart Title"
            dataSource: "SQL query or data source"
        }
    }
}
```

## Advanced Features

### Parallel Processing
```bpml
parallelGateway SplitTasks

userTask Task1 { /* ... */ }
userTask Task2 { /* ... */ }

parallelGateway JoinTasks {
    joinType: all
}
```

### Conditional Routing
```bpml
exclusiveGateway DecisionPoint {
    if (condition1) -> Path1
    if (condition2) -> Path2
    defaultFlow -> DefaultPath
}
```

### Service Integration
```bpml
serviceTask CallService {
    implementation: "ServiceName.methodName"
    input: inputData
    output: outputData
    retryCount: 3
    timeout: 30000
    onSuccess -> NextStep
    onFailure -> ErrorHandler
}
```

### Form Validation
```bpml
form FormName {
    fields: {
        email: email required
        age: number required
    }
    validation: {
        email: email()
        age: min(18)
    }
}
```

## Examples

The `examples/` directory contains complete BPML process definitions:

1. **Order Management** (`order_management.bpml`)
   - E-commerce order processing
   - Inventory management
   - Payment processing
   - Shipping coordination

2. **Employee Onboarding** (`employee_onboarding.bpml`)
   - HR document collection
   - IT account setup
   - Workspace preparation
   - Manager coordination

3. **Document Approval** (`document_approval.bpml`)
   - Multi-level approval chains
   - Legal and compliance review
   - Revision tracking
   - Escalation handling

## Integration with Generators

BPML is designed to work with code generators that can produce:
- **Spring Boot Applications**: REST APIs, JPA entities, security configuration
- **React Applications**: Forms, dashboards, process monitoring
- **Database Schemas**: Entity tables, relationship constraints
- **Docker Configurations**: Containerized deployment

## Best Practices

1. **Process Design**
   - Start with simple processes and add complexity gradually
   - Use clear, descriptive names for all elements
   - Include proper error handling and escalation paths

2. **Entity Modeling**
   - Follow normalization principles
   - Use appropriate data types and constraints
   - Consider future extensibility

3. **Role Definition**
   - Create a clear role hierarchy
   - Use principle of least privilege
   - Document role responsibilities

4. **Form Design**
   - Keep forms simple and focused
   - Use appropriate validation rules
   - Provide clear field labels and help text

## Future Enhancements

- Integration with external workflow engines (Activiti, Camunda)
- Real-time process monitoring and analytics
- Advanced form builders with custom components
- Process simulation and performance analysis
- Multi-tenant process isolation
- Cloud deployment automation

## Contributing

To contribute to BPML development:
1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any language changes
4. Provide example processes for new functionality

## License

BPML is released under the MIT License. See LICENSE file for details.