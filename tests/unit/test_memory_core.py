import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from tools import memory_core

class TestMemoryCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.memory_file = os.path.join(self.test_dir, "TEST_MEMORY.md")
        # Patch the MEMORY_FILE constant
        self.patcher = patch('tools.memory_core.MEMORY_FILE', self.memory_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_append_and_fetch(self):
        """Test writing to and reading from memory."""
        memory_core.append_log("UNIT_TEST", "Test Entry 1", "DEBUG")
        memory_core.append_log("UNIT_TEST", "Test Entry 2", "DEBUG")
        
        context = memory_core.fetch_context()
        self.assertIn("Test Entry 1", context)
        self.assertIn("Test Entry 2", context)
        self.assertIn("[UNIT_TEST]", context)

    def test_fetch_limit(self):
        """Test character limit on fetch."""
        long_text = "A" * 1000
        memory_core.append_log("TEST", long_text)
        
        context = memory_core.fetch_context(char_limit=10)
        # Since fetch_context reads just the characters, and our file has headers/newlines,
        # we should just check the length or if it contains A's.
        # But wait, append_log adds headers.
        # Let's just verify it returns a str of correct length.
        self.assertEqual(len(context), 10)
        self.assertTrue('A' in context)

if __name__ == '__main__':
    unittest.main()
