#!/bin/bash

# Run tests for Python SDK with enhanced output
echo "🧪 Grasp Python SDK Test Runner"
echo "================================"

# Set test environment variables
export GRASP_API_KEY="api-server-test"
export GRASP_BASE_URL="http://localhost:3000"

echo ""
echo "📋 Configuration:"
echo "  GRASP_API_KEY: $GRASP_API_KEY"
echo "  GRASP_BASE_URL: $GRASP_BASE_URL"
echo ""

# Check Python version
echo "🐍 Python version:"
python3 --version

# Install the package in development mode
echo ""
echo "📦 Installing SDK in development mode..."
pip3 install -q -e .

# Install all dev dependencies (including enhanced testing tools)
echo "📚 Installing test dependencies with enhanced output tools..."
pip3 install -q -e ".[dev]"

# Install Playwright for browser automation tests
echo "🎭 Installing Playwright for browser automation tests..."
playwright install chromium --quiet 2>/dev/null || echo "Chromium already installed"

echo ""
echo "🚀 Running tests..."
echo "-------------------"

# Run tests with enhanced output (pytest-sugar provides beautiful output)
pytest tests/ -v

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo "-------------------"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed successfully!"
else
    echo "❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
    echo ""
    echo "💡 Troubleshooting tips:"
    echo "  • Ensure API server is running on http://localhost:3000"
    echo "  • Check if containers are being created properly"
    echo "  • Review error messages above for specific issues"
fi

exit $TEST_EXIT_CODE