#!/bin/bash
set -e

echo "🚂 Railway Build Script Starting..."
echo "======================================"

# Step 1: Install Python dependencies
echo ""
echo "📦 Step 1: Installing Python dependencies..."
echo "Note: Railway auto-installs from requirements_backend_api.txt"
echo "ta-lib is excluded (requires C libraries, fallback implementation available)"
echo "✅ Python dependencies installed (by Railway)"

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

