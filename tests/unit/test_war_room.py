import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open
from io import StringIO

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

from war_room import WarRoomConsole

class TestWarRoomConsole:
    """Test WarRoomConsole class"""

    @pytest.fixture
    def console(self):
        """Fixture for WarRoomConsole instance"""
        return WarRoomConsole()

    def test_initialization(self, console):
        """Test console initializes correctly"""
        assert console.active_persona_name == "Default"
        assert console.current_system_prompt is None
        assert console.running is True

    def test_load_persona_reset(self, console):
        """Test loading 'reset' persona"""
        console.active_persona_name = "OVERWATCH"
        console.current_system_prompt = "Old Prompt"
        
        console.load_persona("reset")
        
        assert console.active_persona_name == "Default"
        assert console.current_system_prompt is None

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="System Prompt Content")
    def test_load_persona_success(self, mock_file, mock_exists, console):
        """Test loading a valid persona"""
        mock_exists.return_value = True
        
        console.load_persona("overwatch")
        
        assert console.active_persona_name == "OVERWATCH"
        assert console.current_system_prompt == "System Prompt Content"
        mock_file.assert_called_once()

    @patch('os.path.exists')
    def test_load_persona_not_found(self, mock_exists, console):
        """Test loading invalid persona"""
        mock_exists.return_value = False
        
        with patch('os.listdir', return_value=['overwatch.md']):
             console.load_persona("invalid_one")
        
        assert console.active_persona_name == "Default"  # Should not change

    @patch('subprocess.run')
    def test_call_advisor_gemini(self, mock_run, console):
        """Test calling Gemini advisor"""
        mock_process = Mock()
        mock_process.stdout = "Gemini Advice"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        output = console.call_advisor("gemini_bridge.py", "help me", "GEMINI", "BLUE")
        
        assert output == "Gemini Advice"
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "gemini_bridge.py" in args[1] # Script
        assert "Advice for: help me" in args[2] # Prompt

    @patch('subprocess.run')
    def test_call_advisor_codex(self, mock_run, console):
        """Test calling Codex advisor"""
        mock_process = Mock()
        mock_process.stdout = "Code Blueprint"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        # Make sure we use the correct constant logic for detecting Codex mode in call_advisor
        # In the implementation, we pass script_path. If it matches strictly constant logic...
        # Let's mock the constants or just rely on path string matching if strictly implemented.
        # The implementation compares `script_path == CODEX_BRIDGE`.
        # So we need to ensure the path string matches what's imported.
        
        from tools.war_room import CODEX_BRIDGE
        output = console.call_advisor(CODEX_BRIDGE, "write code", "CODEX", "BLUE")
        
        assert output == "Code Blueprint"
        args = mock_run.call_args[0][0]
        assert "codex_bridge.py" in args[1]
        assert args[2] == "write code" # No "Advice for:" prefix

    @patch.object(WarRoomConsole, 'execute_claude')
    def test_parse_command_execute(self, mock_execute, console):
        """Test /execute command parsing"""
        console.parse_command("/execute do it now")
        
        mock_execute.assert_called_once()
        args = mock_execute.call_args[0]
        assert args[0] == "do it now" # prompt
        assert args[1] == "" # advice (skipped)
        assert args[2] == "GEMINI" # advisor type default

    @patch.object(WarRoomConsole, 'call_advisor')
    def test_parse_command_consult(self, mock_advisor, console):
        """Test /consult command parsing"""
        console.parse_command("/consult just asking")
        
        mock_advisor.assert_called_once()
        args = mock_advisor.call_args[0]
        assert args[1] == "just asking"

    @patch('os.system')
    def test_clear_screen_windows(self, mock_system, console):
        """Test clear screen on Windows"""
        with patch('os.name', 'nt'):
            console.clear_screen()
            mock_system.assert_called_with('cls')

    @patch.object(WarRoomConsole, 'clear_screen')
    def test_draw_header(self, mock_clear, console):
        """Test draw header"""
        console.draw_header()
        mock_clear.assert_called_once()


    @patch('shutil.which')
    @patch('subprocess.run')
    def test_parse_command_opencode_missing(self, mock_run, mock_which, console):
        """Test /opencode command when binary is missing"""
        mock_which.return_value = None
        console.parse_command("/opencode test")
        
        # Should NOT run subprocess
        mock_run.assert_not_called()
        # Which should be called
        mock_which.assert_called_with("opencode")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_parse_command_opencode_found(self, mock_run, mock_which, console):
        """Test /opencode command when binary exists"""
        mock_which.return_value = "/bin/opencode"
        console.parse_command("/opencode prompt")
        
        mock_run.assert_called_with(["opencode", "prompt"])

    @patch('subprocess.run')
    def test_parse_command_interpreter(self, mock_run, console):
        """Test /interpreter command execution"""
        with patch('sys.executable', 'python_exe'):
            console.parse_command("/interpreter run this")
            
            # Should look for interpreter_bridge.py
            args = mock_run.call_args[0][0]
            assert args[0] == 'python_exe'
            assert 'interpreter_bridge.py' in args[1]
            assert args[2] == 'run this'

    @patch('subprocess.run')
    def test_parse_command_youtube(self, mock_run, console):
        """Test /youtube /vision command execution"""
        with patch('sys.executable', 'python_exe'):
            console.parse_command("/vision https://vimeo.com/video_id")
            
            # Should look for vision_bridge.py (Universal)
            args = mock_run.call_args[0][0]
            assert args[0] == 'python_exe'
            assert 'vision_bridge.py' in args[1]
            assert args[2] == 'https://vimeo.com/video_id'

    @patch('subprocess.run')
    def test_parse_command_harvest(self, mock_run, console):
        """Test /harvest command execution"""
        with patch('sys.executable', 'python_exe'):
            console.parse_command("/harvest https://example.com query")
            
            # Should look for harvester_bridge.py
            args = mock_run.call_args[0][0]
            assert args[0] == 'python_exe'
            assert 'harvester_bridge.py' in args[1]
            assert args[2] == 'https://example.com'
            assert args[3] == 'query'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
