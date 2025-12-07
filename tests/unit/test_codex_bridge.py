import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

import codex_bridge

# Skip OpenAI tests if library not available
SKIP_OPENAI_TESTS = not codex_bridge.OPENAI_AVAILABLE
skip_if_no_openai = pytest.mark.skipif(SKIP_OPENAI_TESTS, reason="OpenAI library not installed")


class TestLoadEnvKey:
    """Test API key loading from various sources"""

    def test_env_var_priority(self):
        """Test environment variable is checked first"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env_key'}):
            key = codex_bridge.load_env_key()
            assert key == 'env_key'

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='OPENAI_API_KEY=dotenv_key\n')
    def test_dotenv_fallback(self, mock_file, mock_exists):
        """Test .env file is checked as fallback"""
        mock_exists.return_value = True

        with patch.dict(os.environ, {}, clear=True):
            key = codex_bridge.load_env_key()
            assert key == 'dotenv_key'

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    def test_global_key_file_fallback(self, mock_expanduser, mock_exists):
        """Test global key file is checked last"""
        mock_expanduser.return_value = '/home/user'

        # Mock .env file not existing, global key file existing
        def exists_side_effect(path):
            if '.env' in path:
                return False
            if '.openai' in path or 'api_key' in path:
                return True
            return False

        mock_exists.side_effect = exists_side_effect

        with patch.dict(os.environ, {}, clear=True):
            with patch('builtins.open', mock_open(read_data='global_key')):
                key = codex_bridge.load_env_key()
                assert key == 'global_key'

    def test_no_key_returns_none(self):
        """Test returns None when no key found"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('os.path.exists', return_value=False):
                key = codex_bridge.load_env_key()
                assert key is None


class TestQueryCodex:
    """Test Codex querying functionality"""

    @patch('codex_bridge.OPENAI_AVAILABLE', False)
    def test_missing_openai_library(self):
        """Test graceful failure when openai library missing"""
        with patch('builtins.print') as mock_print:
            codex_bridge.query_codex("test prompt", "test_key")
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('openai' in str(call).lower() for call in calls)

    @patch('codex_bridge.OPENAI_AVAILABLE', True)
    def test_missing_api_key(self):
        """Test graceful failure when API key missing"""
        with patch('builtins.print') as mock_print:
            codex_bridge.query_codex("test prompt", None)
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('OPENAI_API_KEY not found' in str(call) for call in calls)

    @skip_if_no_openai
    def test_successful_query(self):
        """Test successful Codex query (requires openai library)"""
        from openai import OpenAI

        with patch('codex_bridge.get_context', return_value="Test context"):
            with patch('builtins.print') as mock_print:
                # Create a mock OpenAI client
                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Code response"
                mock_client.chat.completions.create.return_value = mock_response

                with patch('codex_bridge.OpenAI', return_value=mock_client):
                    codex_bridge.query_codex("write a function", "test_key", model="gpt-4o")
                    mock_print.assert_called_with("Code response")

    @skip_if_no_openai
    def test_api_error_handling(self):
        """Test API error handling (requires openai library)"""
        from openai import OpenAI

        with patch('codex_bridge.get_context', return_value="Test context"):
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")

            with patch('codex_bridge.OpenAI', return_value=mock_client):
                with patch('builtins.print') as mock_print:
                    codex_bridge.query_codex("test prompt", "test_key")
                    calls = [str(call) for call in mock_print.call_args_list]
                    assert any('CODEX UPLINK ERROR' in str(call) for call in calls)

    @skip_if_no_openai
    def test_context_injection(self):
        """Test context is injected into query (requires openai library)"""
        from openai import OpenAI

        test_context = "File list: main.py, utils.py"

        with patch('codex_bridge.get_context', return_value=test_context):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Response"
            mock_client.chat.completions.create.return_value = mock_response

            with patch('codex_bridge.OpenAI', return_value=mock_client):
                codex_bridge.query_codex("test prompt", "test_key")

                # Verify create was called with context in user message
                call_args = mock_client.chat.completions.create.call_args
                messages = call_args[1]['messages']
                user_message = messages[1]['content']

                assert test_context in user_message
                assert "TASK: test prompt" in user_message


class TestGetContext:
    """Test context gathering (similar to gemini_bridge)"""

    @patch('os.listdir')
    def test_directory_listing(self, mock_listdir):
        """Test directory listing in context"""
        mock_listdir.return_value = ['file1.py', 'file2.py']
        context = codex_bridge.get_context()

        assert '[SHARED DIRECTORY CONTENT]' in context
        assert 'file1.py' in context

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='Memory content')
    def test_memory_reading(self, mock_file, mock_exists):
        """Test PROJECT_MEMORY.md reading"""
        mock_exists.return_value = True
        context = codex_bridge.get_context()

        assert '[SHARED PROJECT MEMORY' in context


class TestModelSelection:
    """Test model selection"""

    @skip_if_no_openai
    def test_custom_model(self):
        """Test custom model can be specified (requires openai library)"""
        from openai import OpenAI

        with patch('codex_bridge.get_context', return_value="Test context"):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Response"
            mock_client.chat.completions.create.return_value = mock_response

            with patch('codex_bridge.OpenAI', return_value=mock_client):
                codex_bridge.query_codex("test", "key", model="gpt-3.5-turbo")

                call_args = mock_client.chat.completions.create.call_args
                assert call_args[1]['model'] == "gpt-3.5-turbo"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
