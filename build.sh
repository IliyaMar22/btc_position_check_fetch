#!/bin/bash
set -e

echo "🚂 Railway Build Script Starting..."
echo "======================================"

# Ensure Node.js is in PATH (Railway/Nixpacks)
export PATH="/nix/var/nix/profiles/default/bin:$PATH"
if [ -d "$HOME/.nix-profile/bin" ]; then
    export PATH="$HOME/.nix-profile/bin:$PATH"
fi
# Try to find Node.js in common Nix locations
if [ -d "/nix/store" ]; then
    NODE_PATH=$(find /nix/store -name "node" -type f 2>/dev/null | grep -E "nodejs.*bin/node$" | head -1)
    if [ -n "$NODE_PATH" ]; then
        NODE_BIN_DIR=$(dirname "$NODE_PATH")
        export PATH="$NODE_BIN_DIR:$PATH"
        echo "✅ Found Node.js at: $NODE_PATH"
    fi
fi

# Step 1: Install Python dependencies
echo ""
echo "📦 Step 1: Installing Python dependencies..."
echo "Note: Railway auto-installs from requirements_backend_api.txt"
echo "ta-lib is excluded (requires C libraries, fallback implementation available)"
echo "✅ Python dependencies installed (by Railway)"

# Step 2: Install Node.js dependencies
echo ""
echo "📦 Step 2: Installing Node.js dependencies..."

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ ERROR: npm command not found!"
    echo "Checking Node.js installation..."
    echo "PATH: $PATH"
    echo "which node: $(which node || echo 'not found')"
    echo "which npm: $(which npm || echo 'not found')"
    echo ""
    echo "Trying to find Node.js..."
    find /nix -name "npm" 2>/dev/null | head -5 || echo "npm not found in /nix"
    echo ""
    echo "Available commands:"
    ls -la /nix/store/*/bin/npm 2>/dev/null | head -5 || echo "No npm found"
    exit 1
fi

echo "✅ npm found: $(which npm)"
echo "✅ node version: $(node --version)"
echo "✅ npm version: $(npm --version)"

cd btc-trading-frontend
npm install
echo "✅ Node.js dependencies installed"

# Step 3: Build React frontend
echo ""
echo "🏗️  Step 3: Building React frontend..."
npm run build
cd ..
echo "✅ Frontend built successfully"

echo ""
echo "======================================"
echo "✅ Railway Build Complete!"
echo "======================================"

