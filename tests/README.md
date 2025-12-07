# Test Suite Documentation

## Quick Start

### Windows
```powershell
.\run_tests.ps1
```

### Linux/Mac
```bash
./run_tests.sh
```

## Test Organization

```
tests/
├── unit/                       # Unit tests for individual components
│   ├── test_war_room.py        # War Room console tests
│   ├── test_gemini_bridge.py   # Gemini API bridge tests
│   ├── test_codex_bridge.py    # Codex API bridge tests
│   ├── test_log_memory.py      # Memory logging tests
│   ├── test_agent_launchers.sh # Bash launcher tests
│   └── test_agent_launchers.ps1 # PowerShell launcher tests
├── integration/                # End-to-end workflow tests
│   └── test_workflows.py       # Multi-component integration tests
└── fixtures/                   # Test data and mock templates
    └── mock_templates/
```

## Running Tests

### All Tests with Coverage
```bash
# Linux/Mac
./run_tests.sh --coverage

# Windows
.\run_tests.ps1 -Coverage
```

### Unit Tests Only
```bash
# Linux/Mac
./run_tests.sh --unit

# Windows
.\run_tests.ps1 -Unit
```

### Integration Tests Only
```bash
# Linux/Mac
./run_tests.sh --integration

# Windows
.\run_tests.ps1 -Integration
```

### Shell Script Tests
```bash
# Linux/Mac
./run_tests.sh --shell

# Windows
.\run_tests.ps1 -Shell
```

### Manual pytest Invocation
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=tools --cov-report=html

# Specific test file
pytest tests/unit/test_war_room.py -v

# Specific test class
pytest tests/unit/test_war_room.py::TestCommandParsing -v

# Specific test function
pytest tests/unit/test_war_room.py::TestCommandParsing::test_mode_command_parsing -v
```

## Test Categories

### Unit Tests (52 tests)

#### war_room.py (14 tests)
- Command parsing logic
- Mode switching
- Cross-platform compatibility
- Security input validation

#### gemini_bridge.py (16 tests)
- Context gathering
- API key resolution
- .env file parsing
- API interaction

#### log_memory.py (9 tests)
- File operations
- Concurrent writes
- Unicode handling
- Error recovery

#### codex_bridge.py (12 tests)
- API key loading
- Query execution
- Context injection
- Error handling

### Integration Tests (9 tests)
- Memory persistence across components
- Context sharing between bridges
- Multi-agent workflows
- Error recovery scenarios

### Shell Script Tests (14 tests)
- Path traversal prevention
- Input validation
- Template existence checking
- Memory protocol warnings

## Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| log_memory.py | 78% | 85% |
| gemini_bridge.py | 60% | 75% |
| codex_bridge.py | 58% | 75% |
| war_room.py | 18% | 60% |
| **Overall** | **36%** | **70%** |

## Test Fixtures

### Mock Templates
Located in `tests/fixtures/mock_templates/`

Create test templates:
```bash
mkdir -p tests/fixtures/mock_templates
echo "# Test Agent" > tests/fixtures/mock_templates/test-agent.md
```

### Temporary Files
Tests use `tempfile.TemporaryDirectory()` for isolation:
```python
with tempfile.TemporaryDirectory() as tmpdir:
    os.chdir(tmpdir)
    # Test code here
```

## Debugging Failed Tests

### Verbose Output
```bash
pytest tests/ -vv --tb=long
```

### Show Print Statements
```bash
pytest tests/ -v -s
```

### Run Specific Failed Test
```bash
pytest tests/unit/test_codex_bridge.py::TestQueryCodex::test_successful_query -vv
```

### Drop into Debugger on Failure
```bash
pytest tests/ --pdb
```

## Common Test Patterns

### Mocking Subprocess Calls
```python
@patch('subprocess.run')
def test_subprocess_call(mock_run):
    mock_run.return_value = Mock(stdout="output", stderr="")
    # Test code
```

### Mocking File Operations
```python
@patch('builtins.open', new_callable=mock_open, read_data='test content')
def test_file_read(mock_file):
    # Test code
```

### Mocking Environment Variables
```python
with patch.dict(os.environ, {'API_KEY': 'test_key'}):
    # Test code
```

### Testing Exceptions
```python
with pytest.raises(ValueError):
    function_that_should_raise()
```

## Continuous Integration

### GitHub Actions Workflow
Create `.github/workflows/tests.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ --cov=tools --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Security Testing

### Path Traversal Tests
Validates:
- Agent name validation
- Directory traversal prevention
- Shell metacharacter filtering

### Injection Tests
Validates:
- Command injection prevention
- Shell escaping
- Temp file usage for sensitive data

### API Key Leak Tests
```bash
# Check test output doesn't contain API keys
pytest tests/ -v 2>&1 | grep -i "api.*key" || echo "No leaks detected"
```

## Performance Testing

### Benchmark Tests
```python
import time

def test_memory_write_performance():
    start = time.time()
    for i in range(100):
        log_memory.log_entry(f"Entry {i}")
    duration = time.time() - start
    assert duration < 5.0  # Should complete in <5 seconds
```

## Troubleshooting

### Import Errors
Ensure `tools/` is in Python path:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
```

### Windows-Specific Issues
- fcntl not available: Tests skip automatically
- Path separators: Use `os.path.join()`
- Line endings: Git should handle via `.gitattributes`

### Mock Failures
- Verify module imports before mocking
- Check attribute exists: `hasattr(module, 'attribute')`
- Use `spec=True` for strict mocking

## Adding New Tests

1. **Create test file** in appropriate directory
2. **Import test framework**:
   ```python
   import pytest
   from unittest.mock import Mock, patch
   ```
3. **Add test class**:
   ```python
   class TestNewFeature:
       def test_something(self):
           assert True
   ```
4. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

## Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names**: `test_<action>_<expected_result>`
3. **Use fixtures** for common setup
4. **Mock external dependencies** (APIs, file system, subprocesses)
5. **Test edge cases**: empty inputs, large inputs, unicode, errors
6. **Clean up resources**: Use `finally` or context managers
7. **Document complex tests** with docstrings

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)
- [unittest.mock guide](https://docs.python.org/3/library/unittest.mock.html)
- [Test coverage best practices](https://coverage.readthedocs.io/)
