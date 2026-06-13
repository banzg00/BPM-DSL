# BPM-DSL

**FlowGen (process FLOW + code GENerator)** - A domain-specific language for business process management with full-stack code generation.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Overview

BPM-DSL is a complete Domain-Specific Language (DSL) that enables developers to declaratively define business processes and automatically generate full-stack applications. Write your business process logic once in FlowGen and generate:

- **Spring Boot backend** with JPA entities, REST APIs, and a complete process execution engine
- **React frontend** with TypeScript, Material-UI components, and process management interfaces

## Features

- 📝 **Declarative Process Modeling** - Define entities, roles, states, transitions, and workflows
- 🏭 **Full-Stack Code Generation** - Generate complete Spring Boot + React applications
- 🔄 **Process Runtime Engine** - Built-in process execution with state management
- 👥 **Role-Based Access Control** - Define roles with hierarchy and control who can perform actions
- 📊 **Entity Management** - CRUD operations for all defined entities
- ✅ **Task Management** - Workflow task assignment, dependencies, and completion tracking
- 🔍 **Process Tracking** - Monitor running process instances and their states
- 🎯 **Type Safety** - Strong typing with enums and validation
- 📈 **Process Graph Visualization** - Interactive graph view of states, transitions, and task dependencies

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd BPM-DSL

# Install the package
pip install -e .
```

### Usage

1. **Define your business process** in a `.flg` file
2. **Generate Spring Boot backend**:
   ```bash
   textx generate .\flg\examples\example.flg --target springboot -o ./flg/examples/example_output --overwrite --language flg
   ```
3. **Generate React frontend**:
   ```bash
   textx generate .\flg\examples\example.flg --target react -o ./flg/examples/example_output --overwrite --language flg
   ```

## FlowGen Language Syntax

### Basic Structure

A FlowGen file contains project metadata and one or more process definitions:

```flg
project {
    name: InvoiceApprovalSystem
    description: "Automated invoice approval workflow"
    version: "1.0.0"
    author: "FlowGen Team"
}

process InvoiceApproval {
    // Process definition goes here
}
```

### Core Language Elements

#### 1. Entities (Domain Models)

Define business data structures with typed attributes:

```flg
entity Invoice {
    invoiceNumber: string
    vendor: string
    amount: float
    description: string
    category: enum { SUPPLIES, SERVICES, EQUIPMENT, TRAVEL }
    isPaid: boolean
}
```

**Supported Types:**
- `string` - Text data
- `int` - Integer numbers
- `float` - Decimal numbers
- `boolean` - True/false values
- `enum { VALUE1, VALUE2, ... }` - Enumerated types

#### 2. Roles (Process Participants)

Define who can participate in the process, with optional supervision hierarchy:

```flg
role Employee
role Manager supervises Employee
role FinanceTeam
role CFO supervises Manager, FinanceTeam
```

- `supervises` - Defines role hierarchy (optional)

#### 3. States (Process Lifecycle)

Define the possible states a process instance can be in:

```flg
state DraftState
state SubmittedForApprovalState
state ManagerReviewState
state ApprovedState
state RejectedState
state CompletedState
```

#### 4. Tasks (Workflow Items)

Define work items assigned to states, with optional dependencies:

```flg
task InitTask in DraftState by Employee
task CreateInvoice in DraftState by Employee affects Invoice
task SubmitInvoice in DraftState auto affects Invoice depends_on InitTask, CreateInvoice
task ReviewByManager in ManagerReviewState by Manager affects Invoice, ApprovalRecord
```

- `in` - Assigns the task to a specific state
- `by` / `auto` - Specifies which role performs this task, or marks it as automatic
- `affects` - Specifies which entities are modified by this task (optional)
- `depends_on` - Declares dependencies on other tasks (optional). Tasks with no mutual dependencies in the same state run in parallel (fork). A task that `depends_on` multiple tasks creates a join — all dependencies must complete first.

#### 5. Transitions (State Changes)

Define how the process moves between states with role-based authorization:

```flg
transition ManagerApprovesTransition
    from ManagerReviewState
    to ApprovedState
    by Manager

transition RejectInvoiceTransition
    from ManagerReviewState
    to RejectedState
    by Manager
```

### Complete Example

See [flg/examples/example.flg](flg/examples/example.flg) for two complete examples:
- **InvoiceApproval** - Multi-level approval workflow with payment processing
- **EmployeeOnboarding** - New employee onboarding with equipment and training

## Generated Code Structure

### Spring Boot Backend

The generator creates a complete Spring Boot application with:

```
generated_springboot/
└── [project-name]/
    ├── pom.xml                           # Maven configuration
    ├── src/main/java/com/flg/[project]/
    │   ├── [ProjectName]Application.java # Spring Boot entry point
    │   ├── model/                        # JPA Entities
    │   │   ├── [Entity].java            # Your business entities
    │   │   ├── ProcessInstance.java     # Process runtime
    │   │   ├── TaskInstance.java        # Task management
    │   │   └── ProcessDefinition.java   # Process metadata
    │   ├── repository/                   # Spring Data repositories
    │   │   └── [Entity]Repository.java
    │   ├── service/                      # Business logic
    │   │   ├── [Entity]Service.java
    │   │   └── ProcessInstanceService.java
    │   ├── controller/                   # REST API endpoints
    │   │   ├── [Entity]Controller.java  # CRUD operations
    │   │   ├── ProcessInstanceController.java
    │   │   └── TaskController.java
    │   ├── dto/                          # Data transfer objects
    │   │   └── [Entity]DTO.java
    │   ├── mapper/                       # DTO ↔ Entity mappers
    │   │   └── [Entity]Mapper.java
    │   ├── exception/                    # Exception handling
    │   └── config/                       # Configuration
    │       ├── CorsConfig.java
    │       └── ProcessDefinitionLoader.java
    └── src/main/resources/
        └── application.properties
```

**Key Features:**
- ✅ Complete CRUD REST APIs for all entities
- ✅ Process instance management endpoints
- ✅ Task assignment and completion APIs
- ✅ JPA persistence with H2/PostgreSQL support
- ✅ Role-based authorization ready
- ✅ CORS configuration for frontend integration

### React Frontend

The generator creates a complete React + TypeScript application:

```
generated_react/
├── package.json                     # Dependencies (React, MUI, Vite)
├── vite.config.ts
├── tsconfig.json
└── src/
    ├── main.tsx                     # Application entry point
    ├── App.tsx                      # Root component
    ├── AppRoutes.tsx               # Route configuration
    ├── types/
    │   └── types.ts                # TypeScript interfaces & enums
    ├── services/
    │   ├── [Entity]Service.ts      # API client for each entity
    │   ├── ProcessInstanceService.ts
    │   └── TaskService.ts
    ├── pages/
    │   └── [Entity]/               # Per-entity pages
    │       ├── [Entity]List.tsx    # List view with table
    │       ├── [Entity]Dialog.tsx  # Create/Edit modal
    │       └── [Entity]Page.tsx    # Detail page
    └── components/
        ├── HomePage.tsx             # Landing page
        ├── processes/
        │   └── [ProcessName]/
        │       ├── [Process]Dashboard.tsx    # Process overview
        │       ├── ProcessInstanceList.tsx   # Running instances
        │       ├── ProcessInstancePage.tsx   # Instance details
        │       ├── TaskList.tsx              # Workflow tasks
        │       └── ProcessGraph.tsx          # Interactive process graph
        └── shared/
            ├── ProcessTimeline.tsx           # Visual state display
            ├── StartProcessDialog.tsx        # Start new process
            └── StateTransitionDialog.tsx     # State change UI
```

**Key Features:**
- ✅ Material-UI components for modern design
- ✅ Complete CRUD interfaces for all entities
- ✅ Process dashboard with instance monitoring
- ✅ Task list with claim/complete actions
- ✅ Visual process timeline
- ✅ Interactive process graph with state containers, task nodes, transitions, and dependency edges (ReactFlow + dagre)
- ✅ TypeScript type safety
- ✅ Vite for fast development

## Process Runtime Model

The generated applications include a complete process execution engine:

### Process Instance Management

```typescript
interface ProcessInstance {
  id: number;
  processName: string;
  currentState: string;
  status: ProcessStatus;  // RUNNING, COMPLETED, SUSPENDED, TERMINATED, ERROR
  startedAt: string;
  completedAt?: string;
  suspendedAt?: string;
  suspensionReason?: string;
  entityId?: number;      // Linked business entity
  variables: string;      // JSON process variables
}
```

### Task Management

```typescript
interface TaskInstance {
  id: number;
  name: string;
  status: TaskStatus;  // PENDING, IN_PROGRESS, COMPLETED, SKIPPED, CANCELLED
  assignedRole?: string;
  assignedUser?: string;
  createdAt: string;
  completedAt?: string;
  data: string;        // JSON task data
}
```

### Process Definition

Process metadata including states, transitions, roles, and steps are stored as JSON in the `ProcessDefinition` table, loaded automatically at application startup.

## Project Structure

```
BPM-DSL/
├── flg/                          # Main Python package
│   ├── language/                  # DSL language definition
│   │   ├── flg.tx               # TextX grammar
│   │   ├── processors.py         # Semantic validation
│   │   ├── builtins.py           # Type system mappings
│   │   └── custom_model.py       # Custom model classes
│   ├── generator/                 # Code generators
│   │   ├── springboot/           # Spring Boot generator
│   │   │   └── template/         # Jinja2 templates
│   │   ├── react/                # React generator
│   │   │   └── template/         # Jinja2 templates
│   │   └── util/                 # Utilities
│   │       ├── filters.py        # Type mapping filters
│   │       ├── string_format_util.py
│   │       └── file_util.py
│   └── examples/
│       ├── example.flg          # Example processes
│       └── example_output/       # Generated code samples
├── setup.py                       # Package configuration
├── setup.cfg                      # Extended configuration
└── README.md                      # This file
```

## Development Workflow

1. **Define Process Model** - Create your `.flg` file with entities, roles, states, and workflows
2. **Validate Model** - The TextX parser validates syntax and semantics
3. **Generate Backend** - Run the Spring Boot generator
4. **Generate Frontend** - Run the React generator
5. **Run Applications**:
   ```bash
   # Start Spring Boot backend
   cd generated_springboot/[project-name]
   mvn spring-boot:run

   # Start React frontend (in another terminal)
   cd generated_react
   npm install
   npm run dev
   ```
6. **Test Process** - Use the React UI to create entities and start process instances

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **DSL Implementation** | TextX (Python) |
| **Code Generation** | Jinja2 templates |
| **Backend Runtime** | Spring Boot 3, Spring Data JPA |
| **Database** | H2 (dev), PostgreSQL (production) |
| **Frontend Framework** | React 18 + TypeScript |
| **Build Tool (Frontend)** | Vite |
| **UI Components** | Material-UI (MUI) |
| **Process Graph** | ReactFlow, dagre (auto-layout) |
| **Build Tool (Backend)** | Maven |

## Requirements

- Python 3.7+
- TextX
- Java 17+ (for generated Spring Boot apps)
- Node.js 16+ (for generated React apps)
- Maven (for building Spring Boot apps)

## Semantic Validation

The FlowGen language includes comprehensive validation:

- ✅ Project name is required
- ✅ No duplicate process names
- ✅ No duplicate entity names within a process
- ✅ No duplicate role names within a process
- ✅ No duplicate task names within a process
- ✅ Tasks must reference existing roles or be marked `auto`
- ✅ Tasks must reference existing entities and states
- ✅ Task dependencies must reference existing tasks
- ✅ Transitions must reference valid states and roles

Validation errors are caught at parse time before code generation.

## Advanced Features

### Entity-Process Linking

Generated entities include a `processInstanceId` field that links business data to the process instance that created or modified it. This enables:
- Process audit trails
- Data lineage tracking
- Process-specific data queries

### Process State Transitions

Transitions enforce role-based authorization:
```java
// Only managers can approve invoices
transition ManagerApprovesTransition
    from ManagerReviewState
    to ApprovedState
    by Manager
```

The generated backend validates that the user has the required role before allowing the state change.

### Task Assignment

Tasks can be assigned to:
- **Roles** - Any user with that role can claim the task
- **Specific users** - Direct assignment

### Process Graph Visualization

Each generated process includes an interactive graph view accessible from the process dashboard via the "View Process Graph" button. The graph is statically generated at code-generation time (no backend API needed) and displays:

- **State containers** — Colored boxes representing process states (green for initial, blue for intermediate, gray for final)
- **Task nodes** — Inside each state, showing role assignments. Manual tasks have a solid border; automatic tasks have a dashed orange border
- **State transitions** — Bezier edges connecting states, representing the allowed state changes
- **Task dependencies** — Dashed animated edges within a state, showing fork-join semantics. Independent tasks appear in parallel columns; dependent tasks appear to the right

The layout is computed automatically using dagre (left-to-right flow). State containers are draggable for manual arrangement. Built with [ReactFlow](https://reactflow.dev/) and [@dagrejs/dagre](https://github.com/dagrejs/dagre).

### Process Suspension

Process instances can be suspended (paused) and later resumed, useful for:
- Waiting for external events
- Manual intervention required
- Error handling

## Examples

The project includes two complete example processes in [flg/examples/example.flg](flg/examples/example.flg):

### 1. Invoice Approval System
A multi-level approval workflow with:
- 3 entities (Invoice, ApprovalRecord, PaymentInfo)
- 4 roles with hierarchy (Employee, Manager, FinanceTeam, CFO)
- 9 states (Draft → Completed)
- 13 tasks with dependencies and auto tasks
- Branching at 3 points (Manager, Finance, CFO can approve or reject)

### 2. Employee Onboarding
A comprehensive onboarding process with:
- 3 entities (Employee, Equipment, TrainingRecord)
- 5 roles with hierarchy (NewEmployee, HR, ITSupport, Trainer, Supervisor)
- 8 states (New → Active)
- 8 tasks with cross-state dependency chain
- Linear flow with equipment setup and training

## Contributing

Contributions are welcome! Areas for improvement:
- Additional code generators (Angular, Vue, NestJS, etc.)
- Enhanced validation rules
- Testing framework integration
- Process analytics and reporting

## License

MIT License (or your chosen license)

## Credits

Initial project layout generated with `textx startproject`.

Built with [TextX](https://github.com/textX/textX) - a meta-language for building Domain-Specific Languages in Python.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

**BPM-DSL** - Transform business process definitions into production-ready applications.
