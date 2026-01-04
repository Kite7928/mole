#!/bin/bash

# Test runner script

echo "🧪 Running tests..."

# Run tests with coverage
pytest \
  --cov=app \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  -v \
  tests/

echo ""
echo "✅ Tests completed!"
echo "📊 Coverage report generated in htmlcov/"