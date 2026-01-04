# Test runner script for Windows

Write-Host "🧪 Running tests..." -ForegroundColor Green

# Run tests with coverage
pytest `
  --cov=app `
  --cov-report=html `
  --cov-report=term-missing `
  --cov-fail-under=80 `
  -v `
  tests/

Write-Host ""
Write-Host "✅ Tests completed!" -ForegroundColor Green
Write-Host "📊 Coverage report generated in htmlcov/" -ForegroundColor Cyan