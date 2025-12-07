#!/bin/bash
# Test runner script for Unix/Linux/Mac

set -e

echo "================================"
echo "Outlaw Exotix AI Suite - Tests"
echo "================================"
echo ""

# Check if pytest is installed
if ! python3 -m pytest --version &> /dev/null; then
    echo "Installing test dependencies..."
    pip3 install -r requirements-dev.txt
fi

# Parse arguments
COVERAGE=false
UNIT_ONLY=false
INTEGRATION_ONLY=false
SHELL_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --unit|-u)
            UNIT_ONLY=true
            shift
            ;;
        --integration|-i)
            INTEGRATION_ONLY=true
            shift
            ;;
        --shell|-s)
            SHELL_TESTS=true
            shift
            ;;
        --help|-h)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --coverage, -c       Generate coverage report"
            echo "  --unit, -u           Run only unit tests"
            echo "  --integration, -i    Run only integration tests"
            echo "  --shell, -s          Run shell script tests"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run_tests.sh                    # Run all Python tests"
            echo "  ./run_tests.sh --coverage         # Run all tests with coverage"
            echo "  ./run_tests.sh --unit             # Run only unit tests"
            echo "  ./run_tests.sh --shell            # Run Bash tests"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run shell tests if requested
if [ "$SHELL_TESTS" = true ]; then
    echo "Running Bash agent launcher tests..."
    bash tests/unit/test_agent_launchers.sh
    exit $?
fi

# Build pytest command
PYTEST_CMD="python3 -m pytest"

if [ "$UNIT_ONLY" = true ]; then
    PYTEST_CMD="$PYTEST_CMD tests/unit/"
elif [ "$INTEGRATION_ONLY" = true ]; then
    PYTEST_CMD="$PYTEST_CMD tests/integration/"
else
    PYTEST_CMD="$PYTEST_CMD tests/"
fi

PYTEST_CMD="$PYTEST_CMD -v --tb=short"

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=tools --cov-report=term --cov-report=html"
    echo "Coverage report will be generated in htmlcov/"
fi

# Run tests
echo "Running tests..."
echo "Command: $PYTEST_CMD"
echo ""

eval $PYTEST_CMD
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✓ All tests passed!"
else
    echo ""
    echo "✗ Some tests failed (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE
