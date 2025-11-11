#!/bin/bash

# Publish script for Grasp Python SDK
# This script builds and publishes the package to PyPI

set -e  # Exit on error

echo "🚀 Grasp Python SDK Publisher"
echo "============================="
echo ""

# Check current version
CURRENT_VERSION=$(python3 -c "import toml; print(toml.load('pyproject.toml')['project']['version'])" 2>/dev/null || grep "^version" pyproject.toml | cut -d'"' -f2)
echo "📦 Current version: $CURRENT_VERSION"
echo ""

# Confirm version
read -p "Is this the correct version to publish? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted. Please update version in pyproject.toml first."
    exit 1
fi

# Clean old builds
echo "🧹 Cleaning old builds..."
rm -rf dist/ build/ *.egg-info/ src/*.egg-info/

# Install/upgrade build tools
echo "📚 Installing build tools..."
pip3 install --upgrade build twine -q

# Build the package
echo "🔨 Building package..."
python3 -m build

# Check the distribution
echo "✅ Checking distribution..."
twine check dist/*

# Show what will be uploaded
echo ""
echo "📋 Files to be uploaded:"
ls -lh dist/
echo ""

# Ask for confirmation
read -p "Do you want to upload to Test PyPI first? (recommended) (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to Test PyPI..."
    twine upload --repository testpypi dist/*

    echo ""
    echo "✅ Uploaded to Test PyPI!"
    echo "Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ grasp-sdk==$CURRENT_VERSION"
    echo ""

    read -p "Continue to upload to production PyPI? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Published to Test PyPI only. Test it first!"
        exit 0
    fi
fi

# Final confirmation
echo "⚠️  WARNING: This will publish to production PyPI!"
read -p "Are you sure you want to publish version $CURRENT_VERSION to PyPI? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted."
    exit 1
fi

# Upload to PyPI
echo "📤 Uploading to PyPI..."
twine upload dist/*

echo ""
echo "🎉 Successfully published grasp-sdk version $CURRENT_VERSION!"
echo ""
echo "📝 Next steps:"
echo "  1. Create git tag: git tag v$CURRENT_VERSION"
echo "  2. Push tag: git push origin v$CURRENT_VERSION"
echo "  3. Create GitHub release"
echo ""
echo "Install with: pip install grasp-sdk==$CURRENT_VERSION"