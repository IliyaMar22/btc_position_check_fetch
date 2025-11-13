#!/bin/bash
set -e

echo "🚂 Railway Build Script Starting..."
echo "======================================"

# Step 1: Install Python dependencies
echo ""
echo "📦 Step 1: Installing Python dependencies..."
python3 -m pip install --upgrade pip

# Install dependencies from requirements file (excluding ta-lib for now)
echo "Installing main dependencies..."
python3 -m pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 websockets==12.0 pandas==2.1.3 numpy==1.26.2 requests==2.31.0 aiohttp==3.9.1 matplotlib==3.8.2 python-binance==1.0.19 "ccxt>=4.0.0"

# Try to install ta-lib (optional, may fail if C libraries not available)
echo "Attempting to install ta-lib (optional)..."
set +e  # Temporarily disable exit on error
python3 -m pip install ta-lib==0.4.28
TA_LIB_STATUS=$?
set -e  # Re-enable exit on error
if [ $TA_LIB_STATUS -ne 0 ]; then
    echo "⚠️  ta-lib installation failed (this is OK, fallback implementation available)"
fi

echo "✅ Python dependencies installed"

# Step 2: Install Node.js dependencies
echo ""
echo "📦 Step 2: Installing Node.js dependencies..."
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

