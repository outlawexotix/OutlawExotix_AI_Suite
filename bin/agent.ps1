param (
    [Parameter(Mandatory=$true)]
    [string]$Name,
    [Parameter(ValueFromRemainingArguments=$true)]
    $RemainingArgs
)

# Input validation: prevent path traversal
if ($Name -match '[/\\.]') {
    Write-Error "Agent name contains invalid characters (path traversal attempt)"
    exit 1
}

$TemplatePath = "C:\Users\penne\.claude\templates\$Name.md"
$MemoryProtocolPath = "C:\Users\penne\.claude\memory_protocol.md"

if (-not (Test-Path $TemplatePath)) {
    Write-Error "Agent template ''$Name'' not found at $TemplatePath"
    exit 1
}

if (-not (Test-Path $MemoryProtocolPath)) {
    Write-Warning "Memory protocol not found at $MemoryProtocolPath"
}

# Combine the Agent Persona with the Memory Protocol
$AgentPersona = Get-Content -Path $TemplatePath -Raw
$MemoryProtocol = Get-Content -Path $MemoryProtocolPath -Raw
$CombinedSystemPrompt = "$AgentPersona`n$MemoryProtocol"

Write-Host "Deploying Agent: $Name (with Mnemosyne Memory)" -ForegroundColor Cyan

# Pass the combined system prompt to Claude
& "C:\Users\penne\.local\bin\claude.exe" --system-prompt $CombinedSystemPrompt @RemainingArgs
