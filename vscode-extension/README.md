# BPML Language Support for VSCode

Language support for **Business Process Modeling Language (BPML)** in Visual Studio Code.

## Features

- **Syntax Highlighting** - Full keyword and syntax highlighting for `.bpml` files
- **Code Snippets** - Useful snippets for quick scaffolding of BPML constructs
- **Auto-completion** - Bracket and quote auto-closing
- **Code Folding** - Fold/unfold code blocks
- **Comment Support** - Line comments with `//`

## Syntax Highlighting

The extension provides syntax highlighting for all BPML language constructs:

- **Keywords**: `project`, `process`, `entity`, `role`, `state`, `task`, `transition`
- **Modifiers**: `name`, `description`, `version`, `author`, `supervises`, `from`, `to`, `by`, `in`, `affects`, `depends_on`, `auto`
- **Types**: `int`, `float`, `string`, `boolean`, `enum`
- **Strings**: Double-quoted strings with escape character support
- **Comments**: Line comments starting with `//`

## Code Snippets

Type the following prefixes and press `Tab` to insert code templates:

| Prefix | Description |
|--------|-------------|
| `project` | Project definition block |
| `process` | Process definition block |
| `entity` | Entity definition |
| `entity-enum` | Entity with enum field |
| `role` | Simple role definition |
| `role-supervises` | Role with supervision |
| `state` | State definition |
| `task` | Task definition |
| `task-affects` | Task that affects entities |
| `task-depends` | Task with dependencies |
| `task-auto` | Automatic task |
| `transition` | Transition definition |
| `bpml-template` | Complete BPML file template |

## Example Usage

Create a new file with `.bpml` extension and start typing:

```bpml
project {
    name: InvoiceApprovalSystem
    description: "Automated invoice approval workflow"
    version: "1.0.0"
    author: "BPML Team"
}

process InvoiceApproval {
    // Entities
    entity Invoice {
        invoiceNumber: string
        amount: float
        status: enum { PENDING, APPROVED, REJECTED }
    }

    // Roles
    role Employee
    role Manager supervises Employee

    // States
    state DraftState
    state ApprovedState

    // Tasks
    task CreateInvoice in DraftState by Employee affects Invoice
    task ReviewInvoice in DraftState by Manager affects Invoice depends_on CreateInvoice

    // Transitions
    transition ApproveTransition
        from DraftState
        to ApprovedState
        by Manager
}
```

## Installation

### From Source

1. Copy the `vscode-extension` folder to your VSCode extensions directory:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\`
   - **macOS/Linux**: `~/.vscode/extensions/`

2. Rename the folder to `bpml-language-support-0.1.0`

3. Reload VSCode

### Package as VSIX (Recommended)

1. Install `vsce` (Visual Studio Code Extension Manager):
   ```bash
   npm install -g @vscode/vsce
   ```

2. Navigate to the extension directory:
   ```bash
   cd vscode-extension
   ```

3. Package the extension:
   ```bash
   vsce package
   ```

4. Install the generated `.vsix` file in VSCode:
   - Open VSCode
   - Go to Extensions (`Ctrl+Shift+X` or `Cmd+Shift+X`)
   - Click on the `...` menu → `Install from VSIX...`
   - Select the generated `.vsix` file

## Development

To modify or extend the extension:

1. **Syntax Highlighting**: Edit `syntaxes/bpml.tmLanguage.json`
2. **Snippets**: Edit `snippets/bpml.json`
3. **Language Features**: Edit `language-configuration.json`

After making changes, reload VSCode to see updates.

## About BPML

BPML (Business Process Modeling Language) is a domain-specific language for defining business processes that can generate full-stack applications (Spring Boot + React).

For more information about BPML, visit the main project repository.

## License

MIT

## Contributing

Contributions are welcome! Please submit issues and pull requests to improve the extension.
