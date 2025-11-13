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

# Check if Railway created a venv
if [ -d "/opt/venv" ]; then
    echo "Using Railway venv at /opt/venv"
    /opt/venv/bin/pip install --upgrade pip
    /opt/venv/bin/pip install -r requirements_backend_api.txt
    PYTHON_CMD="/opt/venv/bin/python3"
else
    echo "Using system Python"
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements_backend_api.txt
    PYTHON_CMD="python3"
fi

# Verify critical dependencies are installed
echo "Verifying Python dependencies..."
$PYTHON_CMD -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__} installed')" || echo "❌ FastAPI not found!"
$PYTHON_CMD -c "import uvicorn; print(f'✅ Uvicorn installed')" || echo "❌ Uvicorn not found!"
$PYTHON_CMD -c "import pandas; print(f'✅ Pandas {pandas.__version__} installed')" || echo "❌ Pandas not found!"

echo "✅ Python dependencies installed"

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

