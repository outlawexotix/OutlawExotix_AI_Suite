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
        mock_response.prompt_feedback.block_reason = None # Explicitly not blocked
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




class TestOAuthFlow:
    """Test functionality of authenticate_oauth()"""

    @patch('gemini_bridge.OAUTH_AVAILABLE', True)
    @patch('os.path.exists')
    def test_oauth_load_saved_token(self, mock_exists):
        """Test loading credentials from token.json"""
        mock_exists.side_effect = lambda f: f == 'token.json'
        
        with patch('gemini_bridge.Credentials.from_authorized_user_file') as mock_creds:
            mock_creds.return_value = Mock(valid=True)
            creds = gemini_bridge.authenticate_oauth()
            
            assert creds.valid is True

    @patch('gemini_bridge.OAUTH_AVAILABLE', True)
    @patch('os.path.exists')
    def test_oauth_trigger_login_flow(self, mock_exists):
        """Test triggering login flow if token.json missing but client_secret.json exists"""
        # token.json missing, client_secret.json present
        mock_exists.side_effect = lambda f: f == 'client_secret.json'
        
        with patch('gemini_bridge.InstalledAppFlow.from_client_secrets_file') as mock_flow_cls:
            mock_flow = Mock()
            mock_flow_cls.return_value = mock_flow
            mock_flow.run_local_server.return_value = MagicMock(to_json=lambda: 'json_token')
            
            with patch('builtins.open', new_callable=mock_open) as mock_file:
                creds = gemini_bridge.authenticate_oauth()
                
                # Check results
                assert creds is not None
                mock_flow.run_local_server.assert_called_once()
                # Should save token
                mock_file.assert_called_with('token.json', 'w')
                mock_file().write.assert_called_with('json_token')

    @patch('gemini_bridge.OAUTH_AVAILABLE', True)
    @patch('os.path.exists')
    def test_oauth_no_files(self, mock_exists):
        """Test returns None if no auth files exist"""
        mock_exists.return_value = False
        creds = gemini_bridge.authenticate_oauth()
        assert creds is None

    @patch('gemini_bridge.OAUTH_AVAILABLE', False)
    def test_oauth_missing_libs(self):
        """Test returns None if libraries missing"""
        creds = gemini_bridge.authenticate_oauth()
        assert creds is None


class TestAuthFlow:
    """Test authentication logic in main()"""
    
    @patch('gemini_bridge.authenticate_oauth') # New mock
    @patch('gemini_bridge.get_intel')
    @patch('gemini_bridge.get_api_key')
    @patch('sys.exit')
    def test_main_oauth_priority_success(self, mock_exit, mock_get_key, mock_get_intel, mock_oauth):
        """Test OAuth is prioritized over ADC"""
        with patch('sys.argv', ['gemini_bridge.py', 'test prompt']):
            mock_oauth.return_value = 'oauth_creds'
            
            with patch('google.auth.default') as mock_adc: # Should not be called/used
                gemini_bridge.main()
                
                # Verify get_intel called with oauth creds
                mock_get_intel.assert_called_with('test prompt', api_key=None, credentials='oauth_creds', model_name='gemini-1.5-flash')
                mock_get_key.assert_not_called()

    @patch('gemini_bridge.authenticate_oauth')
    @patch('gemini_bridge.get_intel')
    @patch('gemini_bridge.get_api_key')
    @patch('sys.exit')
    def test_main_adc_priority_success(self, mock_exit, mock_get_key, mock_get_intel, mock_oauth):
        """Test ADC is used if OAuth fails but ADC available"""
        mock_oauth.return_value = None # OAuth fails
        
        with patch('sys.argv', ['gemini_bridge.py', 'test prompt']):
            # Mock ADC success
            with patch('google.auth.default', return_value=('cred_obj', 'proj')):
                gemini_bridge.main()
                
                # Verify get_intel called with creds
                mock_get_intel.assert_called_with('test prompt', api_key=None, credentials='cred_obj', model_name='gemini-1.5-flash')
                # get_api_key should NOT be called
                mock_get_key.assert_not_called()

    @patch('gemini_bridge.authenticate_oauth')
    @patch('gemini_bridge.get_intel')
    @patch('gemini_bridge.get_api_key')
    @patch('sys.exit')
    def test_main_adc_fail_fallback_success(self, mock_exit, mock_get_key, mock_get_intel, mock_oauth):
        """Test fallback to API key if ADC and OAuth fail"""
        mock_oauth.return_value = None
        
        with patch('sys.argv', ['gemini_bridge.py', 'test prompt']):
             # Mock ADC failure (ImportError)
            with patch('google.auth.default', side_effect=ImportError("No module")):
                # Mock API Key success
                mock_get_key.return_value = 'fallback_key'
                
                gemini_bridge.main()
                
                # Verify get_intel called with API Key
                mock_get_intel.assert_called_with('test prompt', api_key='fallback_key', credentials=None, model_name='gemini-1.5-flash')

    @patch('gemini_bridge.authenticate_oauth')
    @patch('gemini_bridge.get_intel')
    @patch('gemini_bridge.get_api_key')
    @patch('sys.exit')
    def test_main_all_fail_errors(self, mock_exit, mock_get_key, mock_get_intel, mock_oauth):
        """Test failure when all methods fail"""
        mock_oauth.return_value = None

        with patch('sys.argv', ['gemini_bridge.py', 'test prompt']):
            with patch('google.auth.default', side_effect=Exception("ADC Broken")):
                mock_get_key.return_value = None
                
                gemini_bridge.main()
                
                # Should exit
                mock_exit.assert_called_with(1)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
