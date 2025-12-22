# Projects Directory

This directory is designed to hold your individual projects and workspaces when using the Outlaw Exotix AI Suite.

## Purpose

The `projects/` folder serves as a dedicated workspace for:
- **Active Development Projects** - Your ongoing coding projects that utilize the War Room agents
- **Research & Analysis** - Investigation results from the OVERWATCH and APEX ANALYST agents
- **Security Audits** - Reports and findings from ETHICAL HACKER assessments
- **Code Reviews** - AUDIT results and quality control documentation
- **Organized Workspaces** - Keep your work separate from the AI Suite's core tools

## Usage

Each project should have its own subdirectory:

```
projects/
├── my-web-app/
│   ├── src/
│   ├── tests/
│   └── README.md
├── security-audit-2024/
│   ├── findings/
│   ├── reports/
│   └── README.md
└── research-notes/
    └── analysis.md
```

## Agent Integration

When running agents, you can direct them to work within specific project folders:

```powershell
# Navigate to your project
cd projects/my-web-app

# Run an agent in context
agent overwatch -p "Analyze this application structure"
agent code-auditor -p "Review the src directory"
```

## Best Practices

1. **One Project Per Directory** - Keep projects isolated for clarity
2. **Use Descriptive Names** - Make project folders easy to identify
3. **Document Your Work** - Include a README.md in each project
4. **Version Control** - Initialize git repositories within individual projects
5. **Clean Up** - Archive or remove completed/abandoned projects

## Git Considerations

By default, the contents of your projects are **not ignored** by git. If you want to keep project work private or separate:

1. **Option 1**: Add specific project folders to `.gitignore`:
   ```
   projects/my-private-project/
   ```

2. **Option 2**: Use separate git repositories within each project folder:
   ```bash
   cd projects/my-web-app
   git init
   ```

3. **Option 3**: Add a global pattern to ignore certain file types in projects:
   ```
   projects/**/*.env
   projects/**/node_modules/
   projects/**/__pycache__/
   ```

## Getting Started

Create your first project:

```bash
mkdir projects/my-first-project
cd projects/my-first-project
echo "# My First Project" > README.md
```

Then summon an agent to help:

```powershell
agent commander -p "Help me initialize a Python project in projects/my-first-project"
```

---

**Happy Building! 🚀**
