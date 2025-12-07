# Test runner script for Windows PowerShell

param(
    [switch]$Coverage,
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Shell,
    [switch]$Help
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Outlaw Exotix AI Suite - Tests" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Show help
if ($Help) {
    Write-Host "Usage: .\run_tests.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Coverage       Generate coverage report"
    Write-Host "  -Unit           Run only unit tests"
    Write-Host "  -Integration    Run only integration tests"
    Write-Host "  -Shell          Run PowerShell script tests"
    Write-Host "  -Help           Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run_tests.ps1                    # Run all Python tests"
    Write-Host "  .\run_tests.ps1 -Coverage          # Run all tests with coverage"
    Write-Host "  .\run_tests.ps1 -Unit              # Run only unit tests"
    Write-Host "  .\run_tests.ps1 -Shell             # Run PowerShell tests"
    exit 0
}

# Check if pytest is installed
try {
    python -m pytest --version | Out-Null
} catch {
    Write-Host "Installing test dependencies..." -ForegroundColor Yellow
    pip install -r requirements-dev.txt
}

# Run shell tests if requested
if ($Shell) {
    Write-Host "Running PowerShell agent launcher tests..." -ForegroundColor Yellow
    & .\tests\unit\test_agent_launchers.ps1
    exit $LASTEXITCODE
}

# Build pytest command
$PytestCmd = "python -m pytest"

if ($Unit) {
    $PytestCmd += " tests\unit\"
} elseif ($Integration) {
    $PytestCmd += " tests\integration\"
} else {
    $PytestCmd += " tests\"
}

$PytestCmd += " -v --tb=short"

if ($Coverage) {
    $PytestCmd += " --cov=tools --cov-report=term --cov-report=html"
    Write-Host "Coverage report will be generated in htmlcov\" -ForegroundColor Yellow
}

# Run tests
Write-Host "Running tests..." -ForegroundColor Yellow
Write-Host "Command: $PytestCmd" -ForegroundColor Gray
Write-Host ""

Invoke-Expression $PytestCmd
$ExitCode = $LASTEXITCODE

Write-Host ""
if ($ExitCode -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed (exit code: $ExitCode)" -ForegroundColor Red
}

exit $ExitCode
