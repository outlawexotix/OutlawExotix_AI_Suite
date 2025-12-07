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


class TestAuthentication:
    """Test Application Default Credentials authentication"""

    @patch('builtins.print')
    def test_get_intel_no_credentials(self, mock_print):
        """Test error message when no credentials provided"""
        gemini_bridge.get_intel("test prompt", credentials=None)
        
        # Check that error message was printed
        calls = [str(call) for call in mock_print.call_args_list]
        assert any('ERROR: No valid credentials found' in str(call) for call in calls)
        assert any('gcloud auth application-default login' in str(call) for call in calls)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch('builtins.print')
    def test_get_intel_with_credentials(self, mock_print, mock_model_class, mock_configure):
        """Test successful query with valid credentials"""
        mock_creds = Mock()
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Test response"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        gemini_bridge.get_intel("test prompt", credentials=mock_creds)
        
        mock_configure.assert_called_once_with(credentials=mock_creds)
        mock_model.generate_content.assert_called_once()

    @patch('google.generativeai.configure', side_effect=Exception("Auth error"))
    @patch('builtins.print')
    def test_get_intel_auth_error(self, mock_print, mock_configure):
        """Test handling of authentication errors"""
        mock_creds = Mock()
        gemini_bridge.get_intel("test prompt", credentials=mock_creds)
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any('Failed to configure Gemini' in str(call) for call in calls)
        assert any('gcloud auth application-default login' in str(call) for call in calls)

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    @patch('builtins.print')
    def test_get_intel_api_error(self, mock_print, mock_model_class, mock_configure):
        """Test handling of API errors during query"""
        mock_creds = Mock()
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API error")
        mock_model_class.return_value = mock_model
        
        gemini_bridge.get_intel("test prompt", credentials=mock_creds)
        
        calls = [str(call) for call in mock_print.call_args_list]
        assert any('GEMINI UPLINK ERROR' in str(call) for call in calls)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
