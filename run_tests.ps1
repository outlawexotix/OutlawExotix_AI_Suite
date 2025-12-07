Write-Host "Running Outlaw Exotix AI Suite Tests..." -ForegroundColor Cyan
python -m pytest tests/ -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
}
else {
    Write-Host "✗ Tests failed!" -ForegroundColor Red
}
exit $LASTEXITCODE
