import os
import sys
import argparse
import subprocess
from pathlib import Path

def validate_path(path_str):
    """
    Validates the provided path for security concerns.
    Returns the resolved absolute path or raises ValueError.
    """
    if not path_str:
        raise ValueError("Path cannot be empty")
    
    # Convert to Path object
    try:
        path = Path(path_str).resolve()
    except Exception as e:
        raise ValueError(f"Invalid path format: {e}")
    
    # Security check: Ensure no path traversal attempts
    path_str_normalized = str(path)
    if ".." in path_str or path_str_normalized.startswith("/etc") or path_str_normalized.startswith("/sys"):
        raise ValueError("Path contains potentially unsafe components")
    
    return path

def init_git_repo(repo_path, repo_name=None, description=None, remote_url=None, create_readme=True, create_gitignore=True):
    """
    Initialize a git repository at the specified path.
    
    Args:
        repo_path: Path object where the repository should be initialized
        repo_name: Name of the repository (defaults to directory name)
        description: Description for the README
        remote_url: Optional remote URL to configure as origin
        create_readme: Whether to create a default README.md
        create_gitignore: Whether to create a default .gitignore
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        if not repo_path.exists():
            print(f"Creating directory: {repo_path}")
            repo_path.mkdir(parents=True, exist_ok=True)
        elif not repo_path.is_dir():
            print(f"ERROR: Path exists but is not a directory: {repo_path}")
            return False
        
        # Check if already a git repo
        git_dir = repo_path / ".git"
        if git_dir.exists():
            print(f"WARNING: Directory is already a git repository: {repo_path}")
            response = input("Reinitialize repository? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # Initialize git repository
        print(f"Initializing git repository at: {repo_path}")
        result = subprocess.run(
            ["git", "init"],
            cwd=str(repo_path),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"ERROR: Git initialization failed: {result.stderr}")
            return False
        
        print(result.stdout.strip())
        
        # Determine repo name
        if not repo_name:
            repo_name = repo_path.name
        
        # Create README.md if requested
        if create_readme:
            readme_path = repo_path / "README.md"
            if not readme_path.exists():
                readme_content = f"""# {repo_name}

{description if description else 'A new project repository'}

## Getting Started

This repository was initialized using the Outlaw Exotix AI Suite repo creator.

## Usage

Add your project documentation here.

## License

MIT
"""
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(readme_content)
                print(f"Created: {readme_path}")
            else:
                print(f"README.md already exists, skipping.")
        
        # Create .gitignore if requested
        if create_gitignore:
            gitignore_path = repo_path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
.env
"""
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write(gitignore_content)
                print(f"Created: {gitignore_path}")
            else:
                print(f".gitignore already exists, skipping.")
        
        # Add remote if URL provided
        if remote_url:
            print(f"Adding remote origin: {remote_url}")
            result = subprocess.run(
                ["git", "remote", "add", "origin", remote_url],
                cwd=str(repo_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Check if remote already exists
                if "already exists" in result.stderr:
                    print(f"WARNING: Remote 'origin' already exists. Updating URL...")
                    result = subprocess.run(
                        ["git", "remote", "set-url", "origin", remote_url],
                        cwd=str(repo_path),
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"✓ Remote origin updated to: {remote_url}")
                    else:
                        print(f"ERROR: Failed to update remote: {result.stderr}")
                else:
                    print(f"ERROR: Failed to add remote: {result.stderr}")
            else:
                print(f"✓ Remote origin added: {remote_url}")
        
        # Initial commit
        print("Creating initial commit...")
        
        # Add all files
        subprocess.run(
            ["git", "add", "."],
            cwd=str(repo_path),
            capture_output=True,
            text=True
        )
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(repo_path),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            # Might fail if there are no files to commit
            print(f"Note: {result.stderr.strip()}")
        
        print(f"\n✓ Repository successfully initialized at: {repo_path}")
        print(f"✓ Repository name: {repo_name}")
        if remote_url:
            print(f"✓ Remote origin: {remote_url}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to initialize repository: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Outlaw Exotix Repository Creator - Initialize git repositories from local paths",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python repo_creator.py /home/user/my-project
  python repo_creator.py /home/user/my-project --name "My Project" --description "A cool project"
  python repo_creator.py /home/user/my-project --remote https://github.com/user/my-project.git
  python repo_creator.py ~/Outlaw-Forge --remote https://github.com/outlawexotix/Outlaw-Forge.git
  python repo_creator.py /home/user/my-project --no-readme --no-gitignore
        """
    )
    
    # Positional argument: path
    parser.add_argument(
        "path",
        help="Local file path where the repository should be created"
    )
    
    # Optional arguments
    parser.add_argument(
        "--name", "-n",
        help="Name of the repository (defaults to directory name)"
    )
    
    parser.add_argument(
        "--description", "-d",
        help="Description of the repository for README.md"
    )
    
    parser.add_argument(
        "--remote", "-r",
        help="Remote URL to configure as origin (e.g., https://github.com/user/repo.git)"
    )
    
    parser.add_argument(
        "--no-readme",
        action="store_true",
        help="Skip creating README.md"
    )
    
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Skip creating .gitignore"
    )
    
    args = parser.parse_args()
    
    # Validate and resolve path
    try:
        repo_path = validate_path(args.path)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # Initialize the repository
    success = init_git_repo(
        repo_path,
        repo_name=args.name,
        description=args.description,
        remote_url=args.remote,
        create_readme=not args.no_readme,
        create_gitignore=not args.no_gitignore
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
