# Unit tests for agent.ps1 launcher
# Run with: powershell -ExecutionPolicy Bypass -File tests\unit\test_agent_launchers.ps1

$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$AgentScript = Join-Path $ProjectRoot "bin\agent.ps1"

# Test counters
$TestsRun = 0
$TestsPassed = 0
$TestsFailed = 0

# Test helper functions
function Test-Start {
    param([string]$TestName)
    Write-Host "`nTEST: $TestName" -ForegroundColor Yellow
    $script:TestsRun++
}

function Test-Pass {
    Write-Host "✓ PASS" -ForegroundColor Green
    $script:TestsPassed++
}

function Test-Fail {
    param([string]$Reason)
    Write-Host "✗ FAIL: $Reason" -ForegroundColor Red
    $script:TestsFailed++
}

# Test 1: Agent launcher requires agent name
Test-Start "Agent launcher requires agent name"
try {
    & $AgentScript -ErrorAction Stop 2>&1 | Out-Null
    Test-Fail "Should have failed without agent name"
} catch {
    if ($_ -match "Mandatory") {
        Test-Pass
    } else {
        Test-Fail "Wrong error message"
    }
}

# Test 2: Agent launcher rejects path traversal with dots
Test-Start "Agent launcher rejects path traversal with dots"
try {
    & $AgentScript -Name "..\..\..\etc\passwd" 2>&1 | Out-Null
    Test-Fail "Should reject path with dots"
} catch {
    if ($_ -match "invalid characters" -or $_ -match "path traversal") {
        Test-Pass
    } else {
        Test-Fail "Wrong error for path traversal"
    }
}

# Test 3: Agent launcher rejects forward slashes
Test-Start "Agent launcher rejects forward slashes"
try {
    & $AgentScript -Name "path/to/file" 2>&1 | Out-Null
    Test-Fail "Should reject path with slashes"
} catch {
    if ($_ -match "invalid characters" -or $_ -match "path traversal") {
        Test-Pass
    } else {
        Test-Fail "Wrong error for forward slash"
    }
}

# Test 4: Agent launcher rejects backslashes
Test-Start "Agent launcher rejects backslashes"
try {
    & $AgentScript -Name "path\to\file" 2>&1 | Out-Null
    Test-Fail "Should reject path with backslashes"
} catch {
    if ($_ -match "invalid characters" -or $_ -match "path traversal") {
        Test-Pass
    } else {
        Test-Fail "Wrong error for backslash"
    }
}

# Test 5: Agent launcher validates template exists
Test-Start "Agent launcher validates template exists"
try {
    & $AgentScript -Name "nonexistent-agent-xyz" 2>&1 | Out-Null
    Test-Fail "Should report template not found"
} catch {
    if ($_ -match "not found") {
        Test-Pass
    } else {
        Test-Fail "Wrong error for missing template"
    }
}

# Test 6: Agent launcher checks memory protocol
Test-Start "Agent launcher warns about missing memory protocol"
$TempTemplate = "C:\Users\penne\.claude\templates\test-agent-temp.md"
$MemoryPath = "C:\Users\penne\.claude\memory_protocol.md"

# Create temp template
New-Item -Path (Split-Path $TempTemplate) -ItemType Directory -Force | Out-Null
"# Test Agent" | Out-File -FilePath $TempTemplate -Encoding UTF8

# Backup memory protocol if exists
$MemoryBackup = $null
if (Test-Path $MemoryPath) {
    $MemoryBackup = Get-Content $MemoryPath -Raw
    Remove-Item $MemoryPath
}

# Run and check for warning
try {
    $Output = & $AgentScript -Name "test-agent-temp" -p "--help" 2>&1
    if ($Output -match "Warning.*Memory protocol" -or $Output -match "not found.*memory") {
        Test-Pass
    } else {
        Test-Fail "Should warn about missing memory protocol"
    }
} catch {
    Test-Fail "Unexpected error: $_"
}

# Restore memory protocol if it existed
if ($MemoryBackup) {
    $MemoryBackup | Out-File -FilePath $MemoryPath -Encoding UTF8
}

# Clean up temp template
if (Test-Path $TempTemplate) {
    Remove-Item $TempTemplate
}

# Summary
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Total:  $TestsRun"
Write-Host "Passed: $TestsPassed" -ForegroundColor Green
Write-Host "Failed: $TestsFailed" -ForegroundColor Red
Write-Host "================================" -ForegroundColor Cyan

if ($TestsFailed -eq 0) {
    Write-Host "`nAll tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSome tests failed!" -ForegroundColor Red
    exit 1
}
