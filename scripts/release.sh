#!/bin/bash
# Release md-convert to PyPI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== md-convert Release Script ==="

# Check for required tools
command -v twine >/dev/null 2>&1 || { echo "twine not found. Installing..."; pip install twine; }
command -v build >/dev/null 2>&1 || { echo "build not found. Installing..."; pip install build; }

# Version check
VERSION=$(grep -E '^version = ' "$PROJECT_DIR/pyproject.toml" | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $VERSION"

# Confirm release
read -p "Release version $VERSION to PyPI? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Release cancelled."
    exit 1
fi

# Build distribution
echo "Building distribution..."
cd "$PROJECT_DIR"
rm -rf dist/
python -m build

# Upload to Test PyPI first
echo "Uploading to Test PyPI..."
twine upload --repository testpypi dist/*

# Upload to PyPI
echo "Uploading to PyPI..."
twine upload dist/*

echo ""
echo "=== Release Complete ==="
echo "Version $VERSION has been released."
echo ""
echo "To install from PyPI:"
echo "  pip install md-convert"
echo ""
echo "To install from Test PyPI:"
echo "  pip install --index-url https://test.pypi.org/simple/ md-convert"
