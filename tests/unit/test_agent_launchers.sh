#!/bin/bash
# Unit tests for agent.sh launcher
# Run with: bash tests/unit/test_agent_launchers.sh

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AGENT_SCRIPT="$PROJECT_ROOT/bin/agent.sh"

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test helper functions
test_start() {
    echo -e "${YELLOW}TEST: $1${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_pass() {
    echo -e "${GREEN}✓ PASS${NC}\n"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    echo -e "${RED}✗ FAIL: $1${NC}\n"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# Test 1: Agent launcher requires agent name
test_start "Agent launcher requires agent name"
if bash "$AGENT_SCRIPT" 2>&1 | grep -q "Usage"; then
    test_pass
else
    test_fail "Should show usage message"
fi

# Test 2: Agent launcher rejects path traversal
test_start "Agent launcher rejects path traversal with dots"
if bash "$AGENT_SCRIPT" "../../../etc/passwd" 2>&1 | grep -q "invalid characters"; then
    test_pass
else
    test_fail "Should reject path with dots"
fi

# Test 3: Agent launcher rejects forward slashes
test_start "Agent launcher rejects forward slashes"
if bash "$AGENT_SCRIPT" "path/to/file" 2>&1 | grep -q "invalid characters"; then
    test_pass
else
    test_fail "Should reject path with slashes"
fi

# Test 4: Agent launcher rejects backslashes
test_start "Agent launcher rejects backslashes"
if bash "$AGENT_SCRIPT" "path\\to\\file" 2>&1 | grep -q "invalid characters"; then
    test_pass
else
    test_fail "Should reject path with backslashes"
fi

# Test 5: Agent launcher validates template exists
test_start "Agent launcher validates template exists"
if bash "$AGENT_SCRIPT" "nonexistent-agent-xyz" 2>&1 | grep -q "not found"; then
    test_pass
else
    test_fail "Should report template not found"
fi

# Test 6: Agent launcher accepts valid agent names
test_start "Agent launcher accepts valid alphanumeric names"
# Create a temporary template for testing
TEMP_TEMPLATE="$HOME/.claude/templates/test-agent-temp.md"
mkdir -p "$HOME/.claude/templates"
echo "# Test Agent" > "$TEMP_TEMPLATE"

# Test with --help flag to avoid actual execution
if bash "$AGENT_SCRIPT" "test-agent-temp" --help 2>&1 | grep -q "claude"; then
    test_pass
else
    # Clean up temp file
    rm -f "$TEMP_TEMPLATE"
    test_fail "Should accept valid agent name"
fi

# Clean up temp file
rm -f "$TEMP_TEMPLATE"

# Test 7: Agent launcher warns about missing memory protocol
test_start "Agent launcher warns about missing memory protocol"
TEMP_MEMORY="$HOME/.claude/memory_protocol.md"
MEMORY_BACKUP=""

# Backup memory protocol if it exists
if [ -f "$TEMP_MEMORY" ]; then
    MEMORY_BACKUP=$(cat "$TEMP_MEMORY")
    rm "$TEMP_MEMORY"
fi

# Create temp agent template
echo "# Test Agent" > "$TEMP_TEMPLATE"

# Run and check for warning
if bash "$AGENT_SCRIPT" "test-agent-temp" --help 2>&1 | grep -q "Warning.*Memory protocol"; then
    test_pass
else
    test_fail "Should warn about missing memory protocol"
fi

# Restore memory protocol if it existed
if [ -n "$MEMORY_BACKUP" ]; then
    echo "$MEMORY_BACKUP" > "$TEMP_MEMORY"
fi

# Clean up
rm -f "$TEMP_TEMPLATE"

# Summary
echo "================================"
echo "TEST SUMMARY"
echo "================================"
echo -e "Total:  $TESTS_RUN"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo "================================"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
