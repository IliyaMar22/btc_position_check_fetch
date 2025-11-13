#!/bin/bash
# Start script for Railway deployment

# Use venv Python if Railway created one, otherwise use system Python
if [ -d "/opt/venv" ]; then
    echo "🚀 Starting with Railway venv Python..."
    exec /opt/venv/bin/python3 btc_trading_api.py
else
    echo "🚀 Starting with system Python..."
    exec python3 btc_trading_api.py
fi

