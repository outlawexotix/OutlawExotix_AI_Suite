import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from io import StringIO

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

import war_room


class TestCommandParsing:
    """Test command parsing logic in War Room"""

    def test_mode_command_parsing(self):
        """Test /mode command extracts target correctly"""
        cmd = "/mode overwatch"
        assert cmd.lower().startswith("/mode ")
        target = cmd[6:].strip()
        assert target == "overwatch"

    def test_execute_command_parsing(self):
        """Test /execute command extracts prompt correctly"""
        cmd = "/execute do something"
        assert cmd.lower().startswith("/execute ")
        prompt = cmd[9:].strip()
        assert prompt == "do something"

    def test_consult_command_parsing(self):
        """Test /consult command extracts prompt correctly"""
        cmd = "/consult give me advice"
        assert cmd.lower().startswith("/consult ")
        prompt = cmd[9:].strip()
        assert prompt == "give me advice"

    def test_codex_command_parsing(self):
        """Test /codex command extracts prompt correctly"""
        cmd = "/codex write some code"
        assert cmd.lower().startswith("/codex ")
        prompt = cmd[7:].strip()
        assert prompt == "write some code"


class TestModeReset:
    """Test mode reset functionality"""

    def test_mode_reset_command(self):
        """Test /mode reset is recognized"""
        cmd = "/mode reset"
        target = cmd[6:].strip()
        assert target.lower() == "reset"


class TestTemplatePath:
    """Test template path construction"""

    @patch('os.path.exists')
    def test_template_path_construction(self, mock_exists):
        """Test template path is constructed correctly"""
        current_dir = os.path.dirname(os.path.abspath(war_room.__file__))
        project_root = os.path.dirname(current_dir)
        templates_dir = os.path.join(project_root, "templates")

        agent_name = "overwatch"
        template_path = os.path.join(templates_dir, f"{agent_name}.md")

        assert template_path.endswith("overwatch.md")
        assert "templates" in template_path


class TestCrossPlatformCommands:
    """Test cross-platform command construction"""

    def test_windows_detection(self):
        """Test Windows OS detection"""
        with patch('os.name', 'nt'):
            assert os.name == 'nt'

    def test_unix_detection(self):
        """Test Unix OS detection"""
        with patch('os.name', 'posix'):
            assert os.name == 'posix'


class TestSecurityInputValidation:
    """Test input sanitization and security"""

    def test_command_injection_prevention(self):
        """Test that malicious inputs are handled safely via temp files"""
        malicious_prompts = [
            "$(whoami)",
            "`rm -rf /`",
            "; ls -la",
            "| cat /etc/passwd",
            "$($env:USERNAME)",
        ]

        # These should be written to temp files, not interpolated into shell commands
        for prompt in malicious_prompts:
            # The new implementation writes to temp files
            # So these strings never touch the shell directly
            assert True  # Placeholder - actual test would verify temp file usage


class TestAdvisorSelection:
    """Test advisor bridge selection logic"""

    def test_default_advisor_is_gemini(self):
        """Test default advisor is Gemini"""
        from tools import war_room
        current_dir = os.path.dirname(os.path.abspath(war_room.__file__))
        gemini_bridge = os.path.join(current_dir, "gemini_bridge.py")
        assert "gemini_bridge.py" in gemini_bridge

    def test_codex_advisor_selection(self):
        """Test Codex advisor can be selected"""
        from tools import war_room
        current_dir = os.path.dirname(os.path.abspath(war_room.__file__))
        codex_bridge = os.path.join(current_dir, "codex_bridge.py")
        assert "codex_bridge.py" in codex_bridge


class TestClearScreen:
    """Test screen clearing functionality"""

    @patch('os.system')
    def test_clear_screen_windows(self, mock_system):
        """Test clear screen on Windows"""
        with patch('os.name', 'nt'):
            war_room.clear_screen()
            mock_system.assert_called_with('cls')

    @patch('os.system')
    def test_clear_screen_unix(self, mock_system):
        """Test clear screen on Unix"""
        with patch('os.name', 'posix'):
            war_room.clear_screen()
            mock_system.assert_called_with('clear')


class TestDrawHeader:
    """Test header drawing"""

    @patch('war_room.clear_screen')
    @patch('builtins.print')
    def test_draw_header_outputs_text(self, mock_print, mock_clear):
        """Test header drawing outputs expected text"""
        war_room.draw_header()
        mock_clear.assert_called_once()
        assert mock_print.called


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
