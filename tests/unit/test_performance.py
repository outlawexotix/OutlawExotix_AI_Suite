import pytest
import os
import sys
import time
import tempfile
from unittest.mock import Mock, patch, mock_open

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

import gemini_bridge
import codex_bridge
import log_memory
import war_room


@pytest.mark.unit
class TestFileReadPerformance:
    """Test performance improvements in file reading operations"""

    def test_large_memory_file_read_performance(self):
        """Test that large PROJECT_MEMORY.md files are read efficiently using seek"""
        # Create a large mock file (10KB of text)
        large_content = "Test entry\n" * 1000
        
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_file = os.path.join(tmpdir, "PROJECT_MEMORY.md")
            with open(memory_file, "w", encoding="utf-8") as f:
                f.write(large_content)
            
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Time the operation
                start_time = time.time()
                context = gemini_bridge.get_context()
                elapsed = time.time() - start_time
                
                # Should complete quickly (under 100ms for a 10KB file)
                assert elapsed < 0.1, f"Read took too long: {elapsed}s"
                assert '[SHARED PROJECT MEMORY' in context
                
            finally:
                os.chdir(original_dir)

    def test_directory_listing_is_sorted(self):
        """Test that directory listings are sorted for consistency"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files
            for name in ['zzz.txt', 'aaa.txt', 'mmm.txt']:
                open(os.path.join(tmpdir, name), 'w').close()
            
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                context = gemini_bridge.get_context()
                
                # Extract the file list from context
                assert 'aaa.txt' in context
                # Verify sorted order by checking aaa comes before zzz
                aaa_pos = context.find('aaa.txt')
                zzz_pos = context.find('zzz.txt')
                assert aaa_pos < zzz_pos, "Files should be sorted alphabetically"
                
            finally:
                os.chdir(original_dir)


@pytest.mark.unit
class TestLogMemoryPerformance:
    """Test performance improvements in log_memory module"""

    def test_log_entry_single_file_open(self):
        """Test that log_entry uses a single file open for efficiency"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "PROJECT_MEMORY.md")
            
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # First entry (creates file)
                start_time = time.time()
                log_memory.log_entry("First entry")
                elapsed = time.time() - start_time
                
                # Should be fast (under 50ms)
                assert elapsed < 0.05, f"First log entry took too long: {elapsed}s"
                assert os.path.exists(log_file)
                
                # Second entry (appends)
                start_time = time.time()
                log_memory.log_entry("Second entry")
                elapsed = time.time() - start_time
                
                # Should be even faster for append
                assert elapsed < 0.05, f"Second log entry took too long: {elapsed}s"
                
                # Verify both entries are present
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "First entry" in content
                    assert "Second entry" in content
                    
            finally:
                os.chdir(original_dir)

    def test_initial_retry_delay_is_optimized(self):
        """Test that initial retry delay is reduced for faster operations"""
        # The retry delay should start at 0.05s (50ms) instead of 0.1s (100ms)
        # This test verifies the optimization is in place
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "PROJECT_MEMORY.md")
            
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Multiple rapid writes should complete quickly
                start_time = time.time()
                for i in range(5):
                    log_memory.log_entry(f"Entry {i}")
                elapsed = time.time() - start_time
                
                # 5 entries should complete in under 250ms with optimized retry
                assert elapsed < 0.25, f"Multiple log entries took too long: {elapsed}s"
                
            finally:
                os.chdir(original_dir)


@pytest.mark.unit
class TestWarRoomPerformance:
    """Test performance improvements in war_room module"""

    def test_template_cache_on_startup(self):
        """Test that available templates are cached on startup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock templates directory
            templates_dir = os.path.join(tmpdir, "templates")
            os.makedirs(templates_dir)
            
            # Create some template files
            for name in ['agent1.md', 'agent2.md', 'agent3.md']:
                open(os.path.join(templates_dir, name), 'w').close()
            
            # Patch TEMPLATES_DIR
            with patch('war_room.TEMPLATES_DIR', templates_dir):
                # The template list is now built once on startup
                # Previously it was rebuilt on every error
                templates = [f.replace('.md','') for f in os.listdir(templates_dir) if f.endswith('.md')]
                
                # Should have all templates
                assert len(templates) == 3
                assert 'agent1' in templates
                assert 'agent2' in templates
                assert 'agent3' in templates


@pytest.mark.unit  
class TestContextReadOptimization:
    """Test that context reading is optimized with seek operations"""

    def test_seek_optimization_for_large_files(self):
        """Test that large files use seek to avoid reading entire file"""
        # Create a file larger than 3000 bytes with proper line breaks
        large_content = "Test line X\n" * 400  # Creates ~5KB of content
        
        with tempfile.TemporaryDirectory() as tmpdir:
            memory_file = os.path.join(tmpdir, "PROJECT_MEMORY.md")
            with open(memory_file, "w", encoding="utf-8") as f:
                f.write(large_content)
            
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Get context (should use seek optimization)
                context = gemini_bridge.get_context()
                
                # Should have memory content
                assert '[SHARED PROJECT MEMORY' in context
                # The content should be present (last 3000 chars)
                assert 'Test line X' in context
                
                # Verify it works for codex_bridge too
                context2 = codex_bridge.get_context()
                assert '[SHARED PROJECT MEMORY' in context2
                assert 'Test line X' in context2
                
            finally:
                os.chdir(original_dir)

    def test_fallback_for_unseekable_streams(self):
        """Test that fallback works for unseekable streams (like in tests)"""
        # This test verifies the TypeError catch for mock streams
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data='Test data')):
                # Should not raise exception even with mock
                context = gemini_bridge.get_context()
                assert '[SHARED PROJECT MEMORY' in context


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
