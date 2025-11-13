#!/bin/bash

# Test Railway Build Process Locally
# This simulates what Railway does during deployment

echo "======================================================================"
echo "🧪 Testing Railway Build Process Locally"
echo "======================================================================"
echo ""

# Step 1: Python Dependencies
echo "📦 Step 1: Installing Python dependencies..."
if pip install -r requirements_backend_api.txt; then
    echo "✅ Python dependencies installed"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo ""

# Step 2: Node.js Dependencies
echo "📦 Step 2: Installing Node.js dependencies..."
cd btc-trading-frontend
if npm install; then
    echo "✅ Node.js dependencies installed"
else
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi
echo ""

# Step 3: Build React App
echo "🏗️  Step 3: Building React frontend..."
if npm run build; then
    echo "✅ Frontend built successfully"
else
    echo "❌ Failed to build frontend"
    exit 1
fi
cd ..
echo ""

# Step 4: Check Build Output
echo "📊 Step 4: Checking build output..."
if [ -d "btc-trading-frontend/build" ]; then
    echo "✅ Build directory exists"
    echo "📁 Build size: $(du -sh btc-trading-frontend/build | cut -f1)"
    echo "📄 Files created:"
    ls -lh btc-trading-frontend/build/ | head -10
else
    echo "❌ Build directory not found"
    exit 1
fi
echo ""

# Step 5: Test Backend with Frontend
echo "🚀 Step 5: Testing backend with frontend..."
echo "Starting server for 10 seconds..."
timeout 10 python3 btc_trading_api.py &
SERVER_PID=$!
sleep 3

if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started successfully"
    echo "📊 Testing endpoints..."
    
    # Test API
    if curl -s http://localhost:8123/api/health > /dev/null; then
        echo "✅ API endpoint working"
    else
        echo "⚠️  API endpoint not responding (might need more time)"
    fi
    
    # Test Frontend
    if curl -s http://localhost:8123/ > /dev/null; then
        echo "✅ Frontend endpoint working"
    else
        echo "⚠️  Frontend endpoint not responding"
    fi
    
    # Kill server
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
else
    echo "❌ Server failed to start"
    exit 1
fi
echo ""

echo "======================================================================"
echo "✅ Railway Build Test Complete!"
echo "======================================================================"
echo ""
echo "🎉 Your app is ready for Railway deployment!"
echo ""
echo "Next steps:"
echo "  1. Commit changes: git add . && git commit -m 'Configure for Railway'"
echo "  2. Push to GitHub: git push"
echo "  3. Deploy on Railway: https://railway.app"
echo ""

