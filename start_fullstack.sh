#!/bin/bash

# Bitcoin Trading System - Full Stack Launcher
# This script starts both the backend API and frontend React app

echo "=========================================================================="
echo "🚀 Bitcoin Trading System - Full Stack Launcher"
echo "=========================================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "btc_trading_api.py" ]; then
    echo "${YELLOW}⚠️  Error: btc_trading_api.py not found${NC}"
    echo "Please run this script from the profile directory"
    exit 1
fi

echo ""
echo "${BLUE}📋 Checking dependencies...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "${YELLOW}⚠️  Python 3 not found. Please install Python 3.${NC}"
    exit 1
fi
echo "${GREEN}✅ Python 3 found${NC}"

# Check Node/npm
if ! command -v npm &> /dev/null; then
    echo "${YELLOW}⚠️  npm not found. Please install Node.js.${NC}"
    exit 1
fi
echo "${GREEN}✅ npm found${NC}"

# Check if frontend directory exists
if [ ! -d "btc-trading-frontend" ]; then
    echo "${YELLOW}⚠️  Frontend directory not found${NC}"
    exit 1
fi
echo "${GREEN}✅ Frontend directory found${NC}"

# Check if node_modules exists, if not, install
if [ ! -d "btc-trading-frontend/node_modules" ]; then
    echo ""
    echo "${BLUE}📦 Installing frontend dependencies...${NC}"
    cd btc-trading-frontend
    npm install
    cd ..
    echo "${GREEN}✅ Frontend dependencies installed${NC}"
fi

echo ""
echo "=========================================================================="
echo "${GREEN}🎉 Starting Bitcoin Trading System${NC}"
echo "=========================================================================="
echo ""
echo "${BLUE}Backend API will run on:${NC}      http://localhost:8123"
echo "${BLUE}Frontend will run on:${NC}        http://localhost:3124"
echo "${BLUE}WebSocket will run on:${NC}       ws://localhost:8123/ws"
echo "${BLUE}API Documentation:${NC}           http://localhost:8123/docs"
echo ""
echo "=========================================================================="
echo "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo "=========================================================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "${YELLOW}🛑 Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend in background
echo "${BLUE}🔧 Starting backend API...${NC}"
python3 btc_trading_api.py > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Check if backend is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "${YELLOW}⚠️  Backend failed to start. Check backend.log for details.${NC}"
    exit 1
fi
echo "${GREEN}✅ Backend API started (PID: $BACKEND_PID)${NC}"

# Start frontend in background
echo "${BLUE}🎨 Starting frontend...${NC}"
cd btc-trading-frontend
PORT=3124 npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a bit for frontend to start
sleep 5

echo ""
echo "=========================================================================="
echo "${GREEN}🎉 Both servers are running!${NC}"
echo "=========================================================================="
echo ""
echo "${GREEN}✅ Backend API:${NC}   http://localhost:8123"
echo "${GREEN}✅ Frontend:${NC}      http://localhost:3124"
echo "${GREEN}✅ WebSocket:${NC}     ws://localhost:8123/ws"
echo ""
echo "${BLUE}📊 Check logs:${NC}"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "=========================================================================="
echo "${YELLOW}🌐 Opening browser...${NC}"
echo "=========================================================================="

# Open browser (macOS)
sleep 3
if command -v open &> /dev/null; then
    open http://localhost:3124
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3124
fi

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

