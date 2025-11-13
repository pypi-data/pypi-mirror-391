#!/bin/bash
set -e

echo "🔧 Installing Python and getupandrun CLI for Vercel build..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python 3 not found in PATH. Attempting to install..."
    
    # Try to install Python via package manager (may not work on all systems)
    if command -v apt-get &> /dev/null; then
        echo "📦 Installing Python via apt-get..."
        apt-get update -qq
        apt-get install -y -qq python3 python3-pip python3-venv || echo "⚠️  apt-get install failed (may not have permissions)"
    elif command -v yum &> /dev/null; then
        echo "📦 Installing Python via yum..."
        yum install -y -q python3 python3-pip || echo "⚠️  yum install failed (may not have permissions)"
    elif command -v brew &> /dev/null; then
        echo "📦 Installing Python via Homebrew..."
        brew install python3 || echo "⚠️  brew install failed"
    else
        echo "⚠️  No package manager found. Python may need to be pre-installed."
    fi
fi

# Verify Python installation
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found: $(python3 --version)"
    python3 --version
else
    echo "❌ Python 3 not available. Build may fail if Python is required."
    exit 1
fi

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "⚠️  pip3 not found. Attempting to install..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y -qq python3-pip || echo "⚠️  pip3 install failed"
    fi
fi

# Verify pip installation
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found: $(pip3 --version)"
    pip3 --version
else
    echo "⚠️  pip3 not available. getupandrun installation may fail."
fi

# Install getupandrun CLI
echo "📦 Installing getupandrun CLI..."

# Option 1: Install from PyPI (if published)
if [ -z "$INSTALL_FROM_SOURCE" ]; then
    echo "📥 Installing getupandrun from PyPI..."
    pip3 install --quiet getupandrun || {
        echo "⚠️  PyPI installation failed. Trying local source..."
        INSTALL_FROM_SOURCE=1
    }
fi

# Option 2: Install from local source (if repo includes Python code)
if [ "$INSTALL_FROM_SOURCE" = "1" ] || [ -d "../src" ]; then
    echo "📥 Installing getupandrun from local source..."
    if [ -d "../src" ]; then
        cd ..
        pip3 install --quiet -e . || {
            echo "⚠️  Local source installation failed"
            exit 1
        }
        cd ui
    else
        echo "⚠️  Local source not found. Make sure the repo root is accessible."
        exit 1
    fi
fi

# Verify getupandrun installation
echo "🔍 Verifying getupandrun installation..."
if python3 -m getupandrun.cli.main --version &> /dev/null || python3 -c "import getupandrun" &> /dev/null; then
    echo "✅ getupandrun CLI installed successfully!"
    python3 -m getupandrun.cli.main --version 2>/dev/null || echo "✅ getupandrun module is available"
else
    echo "⚠️  getupandrun verification failed, but installation may have succeeded"
    echo "   The CLI will be called via: python3 -m getupandrun.cli.main"
fi

echo "✅ Python and getupandrun installation complete!"

