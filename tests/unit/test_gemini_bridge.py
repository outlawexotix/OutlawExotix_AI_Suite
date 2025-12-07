import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

import gemini_bridge


class TestGetContext:
    """Test context gathering functionality"""

    @patch('os.listdir')
    def test_get_context_file_listing(self, mock_listdir):
        """Test directory file listing in context"""
        mock_listdir.return_value = ['file1.py', 'file2.py', 'file3.py']
        context = gemini_bridge.get_context()

        assert '[SHARED DIRECTORY CONTENT]' in context
        assert 'file1.py' in context
        assert 'file2.py' in context

    @patch('os.listdir')
    def test_get_context_file_listing_truncation(self, mock_listdir):
        """Test file listing truncates at 50 files"""
        mock_listdir.return_value = [f'file{i}.py' for i in range(100)]
        context = gemini_bridge.get_context()

        assert '[SHARED DIRECTORY CONTENT]' in context
        assert '...' in context  # Truncation indicator

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='# Project Memory\nTest entry 1\nTest entry 2')
    def test_get_context_memory_read(self, mock_file, mock_exists):
        """Test reading PROJECT_MEMORY.md"""
        mock_exists.return_value = True
        context = gemini_bridge.get_context()

        assert '[SHARED PROJECT MEMORY' in context
        mock_file.assert_called_with('PROJECT_MEMORY.md', 'r', encoding='utf-8')

    @patch('os.path.exists')
    def test_get_context_no_memory_file(self, mock_exists):
        """Test behavior when PROJECT_MEMORY.md doesn't exist"""
        mock_exists.return_value = False
        context = gemini_bridge.get_context()

        assert '[SHARED PROJECT MEMORY' not in context

    @patch('os.path.exists')
    @patch('builtins.open', side_effect=Exception("Read error"))
    def test_get_context_memory_read_error(self, mock_file, mock_exists):
        """Test graceful handling of memory read errors"""
        mock_exists.return_value = True
        context = gemini_bridge.get_context()

        assert '[MEMORY READ ERROR]' in context


class TestLoadEnvFile:
    """Test .env file parsing"""

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='GOOGLE_API_KEY=test_key_123\nOTHER_VAR=value')
    def test_load_env_file_success(self, mock_file, mock_exists):
        """Test successful API key extraction from .env"""
        mock_exists.return_value = True
        key = gemini_bridge.load_env_file()

        assert key == 'test_key_123'

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='# Comment\nOTHER_VAR=value')
    def test_load_env_file_no_key(self, mock_file, mock_exists):
        """Test .env file without API key"""
        mock_exists.return_value = True
        key = gemini_bridge.load_env_file()

        assert key is None

    @patch('os.path.exists')
    def test_load_env_file_missing(self, mock_exists):
        """Test behavior when .env doesn't exist"""
        mock_exists.return_value = False
        key = gemini_bridge.load_env_file()

        assert key is None

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='GOOGLE_API_KEY="quoted_key"\n')
    def test_load_env_file_quoted_value(self, mock_file, mock_exists):
        """Test handling of quoted values in .env"""
        mock_exists.return_value = True
        key = gemini_bridge.load_env_file()

        assert key == 'quoted_key'
        assert '"' not in key


class TestGetApiKey:
    """Test API key resolution priority"""

    def test_api_key_priority_cli_flag(self):
        """Test CLI flag has highest priority"""
        args = Mock()
        args.api_key = 'cli_key'
        args.key_file = None

        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'env_key'}):
            key = gemini_bridge.get_api_key(args)
            assert key == 'cli_key'

    def test_api_key_priority_env_var(self):
        """Test environment variable is second priority"""
        args = Mock()
        args.api_key = None
        args.key_file = None

        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'env_key'}):
            with patch('gemini_bridge.load_env_file', return_value=None):
                key = gemini_bridge.get_api_key(args)
                assert key == 'env_key'

    def test_api_key_priority_dotenv(self):
        """Test .env file is third priority"""
        args = Mock()
        args.api_key = None
        args.key_file = None

        with patch.dict(os.environ, {}, clear=True):
            with patch('gemini_bridge.load_env_file', return_value='dotenv_key'):
                key = gemini_bridge.get_api_key(args)
                assert key == 'dotenv_key'

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='file_key')
    def test_api_key_from_file(self, mock_file, mock_exists):
        """Test API key from file"""
        mock_exists.return_value = True
        args = Mock()
        args.api_key = None
        args.key_file = 'keyfile.txt'

        with patch.dict(os.environ, {}, clear=True):
            with patch('gemini_bridge.load_env_file', return_value=None):
                key = gemini_bridge.get_api_key(args)
                assert key == 'file_key'

    def test_api_key_none_when_missing(self):
        """Test returns None when no key found"""
        args = Mock()
        args.api_key = None
        args.key_file = None

        with patch.dict(os.environ, {}, clear=True):
            with patch('gemini_bridge.load_env_file', return_value=None):
                key = gemini_bridge.get_api_key(args)
                assert key is None


class TestGetIntel:
    """Test Gemini API interaction"""

    @patch('gemini_bridge.genai.GenerativeModel')
    @patch('gemini_bridge.genai.configure')
    @patch('gemini_bridge.get_context')
    def test_get_intel_with_api_key(self, mock_context, mock_configure, mock_model):
        """Test get_intel with API key"""
        mock_context.return_value = "Test context"
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_model.return_value.generate_content.return_value = mock_response

        with patch('builtins.print') as mock_print:
            gemini_bridge.get_intel("Test prompt", api_key="test_key")
            mock_configure.assert_called_with(api_key="test_key")
            mock_print.assert_called_with("Test response")

    @patch('builtins.print')
    def test_get_intel_no_auth(self, mock_print):
        """Test get_intel fails gracefully without auth"""
        gemini_bridge.get_intel("Test prompt")
        mock_print.assert_called_with("ERROR: No authentication method provided (API Key or ADC).")

    @patch('gemini_bridge.genai.GenerativeModel')
    @patch('gemini_bridge.genai.configure')
    @patch('gemini_bridge.get_context')
    def test_get_intel_api_error(self, mock_context, mock_configure, mock_model):
        """Test get_intel handles API errors"""
        mock_context.return_value = "Test context"
        mock_model.return_value.generate_content.side_effect = Exception("API Error")

        with patch('builtins.print') as mock_print:
            gemini_bridge.get_intel("Test prompt", api_key="test_key")
            # Check that error was printed
            calls = [str(call) for call in mock_print.call_args_list]
            assert any('GEMINI UPLINK ERROR' in str(call) for call in calls)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
