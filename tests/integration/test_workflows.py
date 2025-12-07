import pytest
import os
import sys
import subprocess
import tempfile
import time
from unittest.mock import patch, MagicMock

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))

import log_memory
import gemini_bridge
import codex_bridge


class TestMemoryPersistence:
    """Integration tests for memory system across components"""

    def test_memory_write_and_read_cycle(self):
        """Test writing to memory and reading back"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Write entry
                log_memory.log_entry("Test integration entry")

                # Verify file exists
                assert os.path.exists('PROJECT_MEMORY.md')

                # Read with gemini context
                context = gemini_bridge.get_context()
                assert "Test integration entry" in context
                assert "[SHARED PROJECT MEMORY" in context

            finally:
                os.chdir(original_dir)

    def test_multiple_agents_write_memory(self):
        """Test multiple agents writing to shared memory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Simulate multiple agents
                log_memory.log_entry("Agent 1: Completed task A")
                log_memory.log_entry("Agent 2: Completed task B")
                log_memory.log_entry("Agent 3: Completed task C")

                # Read memory
                with open('PROJECT_MEMORY.md', 'r') as f:
                    content = f.read()

                assert "Agent 1" in content
                assert "Agent 2" in content
                assert "Agent 3" in content

                # Verify all entries are separate
                assert content.count("##") >= 3  # At least 3 timestamp headers

            finally:
                os.chdir(original_dir)

    def test_memory_context_in_bridges(self):
        """Test memory context is available to both bridges"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Write test memory
                log_memory.log_entry("Critical info: API endpoint is /api/v2")

                # Check Gemini bridge can see it
                gemini_context = gemini_bridge.get_context()
                assert "Critical info" in gemini_context

                # Check Codex bridge can see it
                codex_context = codex_bridge.get_context()
                assert "Critical info" in codex_context

            finally:
                os.chdir(original_dir)


class TestContextSharing:
    """Integration tests for context sharing between components"""

    @patch('os.listdir')
    def test_directory_context_available_to_all(self, mock_listdir):
        """Test directory context is consistent across bridges"""
        mock_listdir.return_value = ['main.py', 'utils.py', 'config.json']

        gemini_context = gemini_bridge.get_context()
        codex_context = codex_bridge.get_context()

        # Both should include directory listing
        assert 'main.py' in gemini_context
        assert 'main.py' in codex_context

        assert '[SHARED DIRECTORY CONTENT]' in gemini_context
        assert '[SHARED DIRECTORY CONTENT]' in codex_context


class TestAgentWorkflows:
    """Integration tests for complete agent workflows"""

    def test_research_to_execution_workflow(self):
        """Test workflow: research -> log finding -> execute based on finding"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Step 1: Research phase (simulated)
                research_finding = "Found vulnerability in authentication module"
                log_memory.log_entry(f"Security audit: {research_finding}")

                # Step 2: Strategy phase reads memory
                context = gemini_bridge.get_context()
                assert research_finding in context

                # Step 3: Execution phase has access to research
                exec_context = codex_bridge.get_context()
                assert research_finding in exec_context

                # Step 4: Log completion
                log_memory.log_entry("Fix applied: Updated authentication module")

                # Verify both entries in memory
                with open('PROJECT_MEMORY.md', 'r') as f:
                    final_memory = f.read()

                assert "Security audit" in final_memory
                assert "Fix applied" in final_memory

            finally:
                os.chdir(original_dir)

    def test_multi_session_memory_accumulation(self):
        """Test memory accumulates across multiple sessions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Session 1
                log_memory.log_entry("Session 1: Installed dependencies")

                # Session 2
                time.sleep(0.1)  # Ensure different timestamps
                log_memory.log_entry("Session 2: Configured settings")

                # Session 3
                time.sleep(0.1)
                log_memory.log_entry("Session 3: Ran tests")

                # Verify chronological order
                with open('PROJECT_MEMORY.md', 'r') as f:
                    content = f.read()

                pos_session1 = content.find("Session 1")
                pos_session2 = content.find("Session 2")
                pos_session3 = content.find("Session 3")

                assert pos_session1 < pos_session2 < pos_session3

            finally:
                os.chdir(original_dir)


class TestMemoryTruncation:
    """Test memory truncation at context limits"""

    def test_large_memory_truncates_in_context(self):
        """Test large memory files are truncated to 3000 chars"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Create large memory file
                with open('PROJECT_MEMORY.md', 'w', encoding='utf-8') as f:
                    f.write("# PROJECT MEMORY LOG\n\n")
                    for i in range(200):
                        f.write(f"## [{i}] Entry {i}\n" + "X" * 50 + "\n")

                # Get context
                context = gemini_bridge.get_context()

                # Context should contain truncated memory (last 3000 chars)
                with open('PROJECT_MEMORY.md', 'r') as f:
                    full_content = f.read()

                # Verify truncation happened
                context_memory = context.split("[SHARED PROJECT MEMORY")[1] if "[SHARED PROJECT MEMORY" in context else ""
                full_memory_length = len(full_content)

                assert full_memory_length > 3000
                # The truncated version should be approximately 3000 chars or less
                assert len(context_memory) < full_memory_length

            finally:
                os.chdir(original_dir)


class TestErrorRecovery:
    """Test error recovery in integrated workflows"""

    def test_memory_write_failure_doesnt_break_workflow(self):
        """Test graceful degradation when memory write fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Create read-only directory to force write failure
                os.mkdir('PROJECT_MEMORY.md')  # Create as directory instead of file

                # Attempt to log should fail gracefully
                try:
                    log_memory.log_entry("This should fail")
                except Exception as e:
                    # Should raise but not crash the system
                    assert "PROJECT_MEMORY.md" in str(e) or "directory" in str(e).lower()

            finally:
                os.chdir(original_dir)

    def test_missing_memory_file_doesnt_break_context(self):
        """Test context works even without memory file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                # Get context without memory file
                context = gemini_bridge.get_context()

                # Should still have directory listing
                assert '[SHARED DIRECTORY CONTENT]' in context
                # But no memory section
                assert '[SHARED PROJECT MEMORY' not in context

            finally:
                os.chdir(original_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
