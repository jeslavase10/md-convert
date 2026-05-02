#!/bin/bash
# Build md-convert for distribution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build"

echo "=== md-convert Build Script ==="
echo "Project directory: $PROJECT_DIR"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf "$DIST_DIR" "$BUILD_DIR"

# Create dist directory
mkdir -p "$DIST_DIR"

# Build wheel
echo "Building wheel..."
cd "$PROJECT_DIR"
pip wheel . -w "$DIST_DIR" --no-deps

# Build with PyInstaller (standalone binary)
echo "Building standalone binary with PyInstaller..."
pip install pyinstaller
pyinstaller \
    --onefile \
    --name md-convert \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR" \
    "$PROJECT_DIR/src/md_converter/__main__.py"

echo ""
echo "=== Build Complete ==="
echo "Output files:"
ls -la "$DIST_DIR"

echo ""
echo "Distribution options:"
echo "  Wheel: $DIST_DIR/*.whl"
echo "  Binary: $DIST_DIR/md-convert"
echo ""
echo "To install the wheel:"
echo "  pip install $DIST_DIR/*.whl"
echo ""
echo "To install the standalone binary:"
echo "  # Linux/macOS"
echo "  sudo cp $DIST_DIR/md-convert /usr/local/bin/"
echo "  # Windows"
echo "  copy $DIST_DIR\\md-convert.exe %PATH%"
