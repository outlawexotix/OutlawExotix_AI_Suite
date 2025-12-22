# Repository Creator Tool - Usage Guide

The `repo_creator.py` tool allows you to initialize git repositories from local paths with automatic configuration of README.md, .gitignore, and remote origins.

## Quick Start

### Basic Usage

Initialize a repository at a given path:
```bash
python tools/repo_creator.py /path/to/your/project
```

### Example: Setting Up Outlaw-Forge

To set up the Outlaw-Forge repository with a remote origin:

```bash
# Navigate to your workspace
cd ~

# Create and initialize the Outlaw-Forge repository
python /path/to/OutlawExotix_AI_Suite/tools/repo_creator.py ~/Outlaw-Forge \
  --name "Outlaw Forge" \
  --description "The Outlaw Forge project repository" \
  --remote https://github.com/outlawexotix/Outlaw-Forge.git
```

This single command will:
1. Create the directory `~/Outlaw-Forge` (if it doesn't exist)
2. Initialize a git repository (`git init`)
3. Create a default README.md with your project name and description
4. Create a .gitignore with common Python exclusions
5. Add the remote origin (`git remote add origin <url>`)
6. Create an initial commit

### Manual Steps Alternative

If you prefer to do it manually (equivalent to the above):

```bash
cd ~/Outlaw-Forge
git init
git remote add origin https://github.com/outlawexotix/Outlaw-Forge.git
# Then create README.md and .gitignore manually
```

## Command Options

### Required Arguments

- `path` - Local file path where the repository should be created

### Optional Arguments

- `--name NAME` or `-n NAME` - Name of the repository (defaults to directory name)
- `--description DESC` or `-d DESC` - Description for the README.md
- `--remote URL` or `-r URL` - Remote URL to configure as origin
- `--no-readme` - Skip creating README.md
- `--no-gitignore` - Skip creating .gitignore

## Usage Examples

### Example 1: Minimal Setup
```bash
python tools/repo_creator.py ~/my-project
```

### Example 2: With Custom Name and Description
```bash
python tools/repo_creator.py ~/my-project \
  --name "My Awesome Project" \
  --description "A revolutionary new tool"
```

### Example 3: With Remote Origin
```bash
python tools/repo_creator.py ~/my-project \
  --remote https://github.com/username/my-project.git
```

### Example 4: Without Auto-Generated Files
```bash
python tools/repo_creator.py ~/my-project \
  --no-readme \
  --no-gitignore
```

### Example 5: Full Configuration (Outlaw-Forge Style)
```bash
python tools/repo_creator.py ~/Outlaw-Forge \
  --name "Outlaw Forge" \
  --description "Advanced AI-powered development tools" \
  --remote https://github.com/outlawexotix/Outlaw-Forge.git
```

## What Gets Created

### README.md
A basic README with:
- Project name as heading
- Description
- Getting Started section
- Usage section
- License section (MIT)

### .gitignore
Python-focused .gitignore with:
- Python bytecode and cache files
- Virtual environment directories
- IDE configuration files
- OS-specific files
- Common project files (.env, .log)

### Git Configuration
- Initialized git repository
- Optional remote origin configuration
- Initial commit (if git user is configured)

## Security Features

The tool includes security validations:
- Path traversal prevention (blocks `..` in paths)
- System directory protection (blocks `/etc`, `/sys`)
- Input validation for all parameters
- Safe subprocess execution

## Troubleshooting

### "Author identity unknown" Error

If you see an error about author identity when creating the initial commit, configure git:

```bash
git config --global user.email "your@email.com"
git config --global user.name "Your Name"
```

Then re-run the tool.

### "Directory is already a git repository"

If the directory already contains a `.git` folder, the tool will ask if you want to reinitialize:
- Press `y` to reinitialize (warning: this resets git history)
- Press `N` to cancel

### Remote Already Exists

If you try to add a remote that already exists, the tool will automatically update the URL instead of failing.

## Integration with War Room

You can call this tool from the War Room console:

```powershell
/execute python tools/repo_creator.py ~/Outlaw-Forge --remote https://github.com/outlawexotix/Outlaw-Forge.git
```

Or use it with an agent:

```bash
agent apex-analyst -p "Initialize a new repo at ~/my-project with remote https://github.com/user/my-project.git"
```

## Next Steps After Repository Creation

After creating your repository, you can:

1. **Add files to your project**
   ```bash
   cd ~/Outlaw-Forge
   # Add your project files
   ```

2. **Push to remote** (if configured)
   ```bash
   git push -u origin main
   # or
   git push -u origin master
   ```

3. **Create branches**
   ```bash
   git checkout -b feature/new-feature
   ```

4. **Continue development**
   ```bash
   # Make changes
   git add .
   git commit -m "Add new feature"
   git push
   ```

## See Also

- Main README: [README.md](../README.md)
- GitHub Setup Guide: [GITHUB_SETUP.md](../GITHUB_SETUP.md)
- War Room Documentation: [CLAUDE.md](../CLAUDE.md)
