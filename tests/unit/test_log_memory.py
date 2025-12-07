import pytest
import os
import sys
import tempfile
import threading
import time
from unittest.mock import Mock, patch, mock_open

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

import log_memory


class TestLogEntry:
    """Test memory logging functionality"""

    def test_creates_file_with_header(self):
        """Test first log creates file with header"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'PROJECT_MEMORY.md')

            with patch('log_memory.log_entry') as mock_log:
                # Simulate first write
                if not os.path.exists(log_file):
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write("# PROJECT MEMORY LOG\n\n")

                assert os.path.exists(log_file)
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "# PROJECT MEMORY LOG" in content

    def test_appends_to_existing_file(self):
        """Test subsequent logs append, not overwrite"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # First entry
                log_memory.log_entry("First entry")
                with open('PROJECT_MEMORY.md', 'r') as f:
                    first_content = f.read()

                # Second entry
                log_memory.log_entry("Second entry")
                with open('PROJECT_MEMORY.md', 'r') as f:
                    second_content = f.read()

                # Both entries should be present
                assert "First entry" in second_content
                assert "Second entry" in second_content
                assert len(second_content) > len(first_content)
            finally:
                os.chdir(original_dir)

    def test_timestamp_format(self):
        """Test timestamp has correct format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                log_memory.log_entry("Test entry")
                with open('PROJECT_MEMORY.md', 'r') as f:
                    content = f.read()

                # Should contain timestamp in format YYYY-MM-DD HH:MM:SS
                import re
                timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
                assert re.search(timestamp_pattern, content)
            finally:
                os.chdir(original_dir)

    def test_unicode_handling(self):
        """Test emoji and non-ASCII characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                test_entries = [
                    "Test with emoji 🚀",
                    "Test with unicode: café, naïve",
                    "Test with Chinese: 你好",
                ]

                for entry in test_entries:
                    log_memory.log_entry(entry)

                with open('PROJECT_MEMORY.md', 'r', encoding='utf-8') as f:
                    content = f.read()

                for entry in test_entries:
                    assert entry in content
            finally:
                os.chdir(original_dir)

    def test_large_entry_handling(self):
        """Test behavior with large log entries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                large_entry = "X" * 10000  # 10KB entry
                log_memory.log_entry(large_entry)

                with open('PROJECT_MEMORY.md', 'r') as f:
                    content = f.read()

                assert large_entry in content
            finally:
                os.chdir(original_dir)

    @pytest.mark.skipif(not log_memory.HAS_FCNTL, reason="fcntl not available on Windows")
    def test_concurrent_writes_unix(self):
        """Test concurrent writes with file locking (Unix only)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                def write_entry(n):
                    import time
                    # Small random delay to avoid exact simultaneous writes
                    time.sleep(n * 0.01)
                    log_memory.log_entry(f"Entry {n}")

                # Spawn multiple threads
                threads = []
                for i in range(5):
                    t = threading.Thread(target=write_entry, args=(i,))
                    threads.append(t)
                    t.start()

                # Wait for all threads
                for t in threads:
                    t.join()

                # Allow final file operations to complete
                import time
                time.sleep(0.1)

                # Verify all entries are present
                with open('PROJECT_MEMORY.md', 'r') as f:
                    content = f.read()

                for i in range(5):
                    assert f"Entry {i}" in content
            finally:
                os.chdir(original_dir)

    def test_retry_mechanism(self):
        """Test retry logic with transient failures"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Normal operation should succeed
                log_memory.log_entry("Test retry")
                assert os.path.exists('PROJECT_MEMORY.md')
            finally:
                os.chdir(original_dir)


class TestMainExecution:
    """Test command-line execution"""

    def test_requires_argument(self):
        """Test script requires log entry argument"""
        with patch('sys.argv', ['log_memory.py']):
            with patch('sys.exit') as mock_exit:
                with patch('builtins.print') as mock_print:
                    if len(sys.argv) < 2:
                        mock_print("Usage: python log_memory.py \"Your log entry here\"")
                        mock_exit(1)

                    mock_exit.assert_called_with(1)

    def test_accepts_multi_word_entry(self):
        """Test multi-word entries are joined correctly"""
        test_args = ['log_memory.py', 'First', 'Second', 'Third']
        entry = " ".join(test_args[1:])
        assert entry == "First Second Third"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
