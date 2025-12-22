import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, call

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

import repo_creator


class TestValidatePath:
    """Test path validation functionality"""

    def test_validates_empty_path(self):
        """Test that empty path raises ValueError"""
        with pytest.raises(ValueError, match="Path cannot be empty"):
            repo_creator.validate_path("")

    def test_validates_path_traversal_dotdot(self):
        """Test that path traversal with .. is blocked"""
        with pytest.raises(ValueError, match="potentially unsafe"):
            repo_creator.validate_path("/home/user/../etc/passwd")

    def test_validates_system_paths(self):
        """Test that system paths like /etc are blocked"""
        with pytest.raises(ValueError, match="potentially unsafe"):
            repo_creator.validate_path("/etc/passwd")

    def test_validates_valid_path(self):
        """Test that valid paths are accepted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = repo_creator.validate_path(tmpdir)
            assert isinstance(path, Path)
            assert path.exists()

    def test_resolves_relative_path(self):
        """Test that relative paths are resolved to absolute"""
        path = repo_creator.validate_path(".")
        assert path.is_absolute()


class TestInitGitRepo:
    """Test git repository initialization"""

    def test_creates_directory_if_not_exists(self):
        """Test that the function creates the directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "new-repo"
            assert not repo_path.exists()
            
            repo_creator.init_git_repo(repo_path)
            
            assert repo_path.exists()
            assert repo_path.is_dir()

    def test_initializes_git_repository(self):
        """Test that .git directory is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            
            repo_creator.init_git_repo(repo_path)
            
            git_dir = repo_path / ".git"
            assert git_dir.exists()
            assert git_dir.is_dir()

    def test_creates_readme_by_default(self):
        """Test that README.md is created by default"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            
            repo_creator.init_git_repo(repo_path, repo_name="Test Repo")
            
            readme = repo_path / "README.md"
            assert readme.exists()
            
            content = readme.read_text()
            assert "# Test Repo" in content

    def test_creates_gitignore_by_default(self):
        """Test that .gitignore is created by default"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            
            repo_creator.init_git_repo(repo_path)
            
            gitignore = repo_path / ".gitignore"
            assert gitignore.exists()
            
            content = gitignore.read_text()
            assert "__pycache__" in content
            assert "*.py[cod]" in content

    def test_skips_readme_when_no_readme_flag(self):
        """Test that README.md is not created when create_readme=False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            
            repo_creator.init_git_repo(repo_path, create_readme=False)
            
            readme = repo_path / "README.md"
            assert not readme.exists()

    def test_skips_gitignore_when_no_gitignore_flag(self):
        """Test that .gitignore is not created when create_gitignore=False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            
            repo_creator.init_git_repo(repo_path, create_gitignore=False)
            
            gitignore = repo_path / ".gitignore"
            assert not gitignore.exists()

    def test_uses_custom_description(self):
        """Test that custom description is used in README"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            description = "This is a custom description"
            
            repo_creator.init_git_repo(repo_path, description=description)
            
            readme = repo_path / "README.md"
            content = readme.read_text()
            assert description in content

    def test_adds_remote_origin(self):
        """Test that remote origin is added when URL provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            remote_url = "https://github.com/user/test-repo.git"
            
            repo_creator.init_git_repo(repo_path, remote_url=remote_url)
            
            # Verify remote was added
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=str(repo_path),
                capture_output=True,
                text=True
            )
            assert remote_url in result.stdout
            assert "origin" in result.stdout

    def test_returns_false_for_non_directory_path(self):
        """Test that function returns False if path exists but is not a directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test-file.txt"
            file_path.write_text("test")
            
            result = repo_creator.init_git_repo(file_path)
            
            assert result is False

    def test_doesnt_overwrite_existing_readme(self):
        """Test that existing README.md is not overwritten"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            repo_path.mkdir()
            
            readme = repo_path / "README.md"
            original_content = "# Original content"
            readme.write_text(original_content)
            
            repo_creator.init_git_repo(repo_path)
            
            assert readme.read_text() == original_content

    def test_doesnt_overwrite_existing_gitignore(self):
        """Test that existing .gitignore is not overwritten"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            repo_path.mkdir()
            
            gitignore = repo_path / ".gitignore"
            original_content = "# Original gitignore"
            gitignore.write_text(original_content)
            
            repo_creator.init_git_repo(repo_path)
            
            assert gitignore.read_text() == original_content

    def test_uses_directory_name_as_default_repo_name(self):
        """Test that directory name is used as repo name when not specified"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "my-awesome-repo"
            
            repo_creator.init_git_repo(repo_path)
            
            readme = repo_path / "README.md"
            content = readme.read_text()
            assert "# my-awesome-repo" in content


class TestMain:
    """Test main function and CLI argument parsing"""

    def test_main_with_valid_path(self):
        """Test main function with valid path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "test-repo")
            
            with patch('sys.argv', ['repo_creator.py', test_path]):
                try:
                    repo_creator.main()
                except SystemExit as e:
                    assert e.code == 0
            
            assert os.path.exists(test_path)

    def test_main_with_name_argument(self):
        """Test main function with --name argument"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "test-repo")
            
            with patch('sys.argv', ['repo_creator.py', test_path, '--name', 'Custom Name']):
                try:
                    repo_creator.main()
                except SystemExit:
                    pass
            
            readme = Path(test_path) / "README.md"
            if readme.exists():
                content = readme.read_text()
                assert "# Custom Name" in content

    def test_main_with_remote_argument(self):
        """Test main function with --remote argument"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "test-repo")
            remote_url = "https://github.com/user/test.git"
            
            with patch('sys.argv', ['repo_creator.py', test_path, '--remote', remote_url]):
                try:
                    repo_creator.main()
                except SystemExit:
                    pass
            
            # Verify remote was configured
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=test_path,
                capture_output=True,
                text=True
            )
            assert remote_url in result.stdout

    def test_main_with_no_readme_flag(self):
        """Test main function with --no-readme flag"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "test-repo")
            
            with patch('sys.argv', ['repo_creator.py', test_path, '--no-readme']):
                try:
                    repo_creator.main()
                except SystemExit:
                    pass
            
            readme = Path(test_path) / "README.md"
            assert not readme.exists()

    def test_main_with_no_gitignore_flag(self):
        """Test main function with --no-gitignore flag"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "test-repo")
            
            with patch('sys.argv', ['repo_creator.py', test_path, '--no-gitignore']):
                try:
                    repo_creator.main()
                except SystemExit:
                    pass
            
            gitignore = Path(test_path) / ".gitignore"
            assert not gitignore.exists()


class TestSecurityFeatures:
    """Test security features of the repo creator"""

    def test_blocks_path_traversal_with_dotdot(self):
        """Test that path traversal attempts are blocked"""
        with pytest.raises(ValueError):
            repo_creator.validate_path("../../../etc/passwd")

    def test_blocks_system_directories(self):
        """Test that system directories are blocked"""
        system_paths = ["/etc/test", "/sys/test"]
        
        for path in system_paths:
            with pytest.raises(ValueError, match="potentially unsafe"):
                repo_creator.validate_path(path)

    def test_handles_git_init_failure_gracefully(self):
        """Test that git init failure is handled gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test-repo"
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr="Git error")
                result = repo_creator.init_git_repo(repo_path)
            
            assert result is False


# Import subprocess for remote test
import subprocess
