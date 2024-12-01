#!/usr/bin/env bash

errors=0

# Run Python tests
echo "Running Python tests..."
uv run pytest -q || errors=$?

# Run JavaScript tests
echo "Running JavaScript tests..."
npm test || errors=$?

exit $errors
