"""
Bitcoin Trading System - FastAPI Backend
========================================
Real-time API with WebSocket support for dynamic updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio
import json
from datetime import datetime
from typing import List, Dict
import logging

from multi_timeframe_position_analyzer import MultiTimeframePositionAnalyzer
from fear_greed_index import FearGreedIndexFetcher
from multi_source_data_fetcher import MultiSourceDataAggregator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BTC Trading System API", version="1.0.0")

# Enable CORS for React frontend
# Configure allowed origins for development and production
import os
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    allowed_origins = [
        "https://*.vercel.app",  # All Vercel deployments
        "https://btc-trading-dashboard.vercel.app",  # Production Vercel
        os.getenv("FRONTEND_URL", ""),  # Custom frontend URL from env
    ]
    # Filter out empty strings
    allowed_origins = [origin for origin in allowed_origins if origin]
else:
    allowed_origins = [
        "http://localhost:3124",
        "http://localhost:3000",
        "http://localhost:3001",
        "*",  # Allow all in development
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Global instances
analyzer = MultiTimeframePositionAnalyzer()
fear_greed_fetcher = FearGreedIndexFetcher()
data_fetcher = MultiSourceDataAggregator()

# Store active WebSocket connections
active_connections: List[WebSocket] = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)


manager = ConnectionManager()


def serialize_position(position: Dict) -> Dict:
    """Convert position data to JSON-serializable format"""
    
    # Convert numpy/pandas types to Python types
    serialized = {
        'timeframe': position['timeframe'],
        'timeframe_name': position['timeframe_name'],
        'timestamp': position['timestamp'].isoformat() if hasattr(position['timestamp'], 'isoformat') else str(position['timestamp']),
        'current_price': float(position['current_price']),
        'recommendation': position['recommendation'],
        'action': position['action'],
        'confidence': position['confidence'],
        'score': int(position['score']),
        'max_score': int(position['max_score']),
        
        # Entry/Exit levels
        'entry': float(position['entry']) if position['entry'] else None,
        'stop_loss': float(position['stop_loss']) if position['stop_loss'] else None,
        'take_profit_1': float(position['take_profit_1']) if position['take_profit_1'] else None,
        'take_profit_2': float(position['take_profit_2']) if position['take_profit_2'] else None,
        'take_profit_3': float(position['take_profit_3']) if position['take_profit_3'] else None,
        'risk_pct': float(position['risk_pct']),
        'reward_pct': float(position['reward_pct']),
        'risk_reward_ratio': float(position['risk_reward_ratio']),
        
        # Technical indicators
        'technical_indicators': {
            'ema_12': float(position['ema_12']),
            'ema_26': float(position['ema_26']),
            'sma_50': float(position['sma_50']),
            'sma_200': float(position['sma_200']) if not pd.isna(position['sma_200']) else None,
            'rsi': float(position['rsi']),
            'macd': float(position['macd']),
            'macd_signal': float(position['macd_signal']),
            'stoch_k': float(position['stoch_k']),
            'bb_upper': float(position['bb_upper']),
            'bb_middle': float(position['bb_middle']),
            'bb_lower': float(position['bb_lower']),
            'atr': float(position['atr']),
            'trend': int(position['trend']),
            'adx': float(position['adx']),
            'volume_ratio': float(position['volume_ratio']),
        },
        
        # Levels
        'support_levels': [float(x) for x in position['support_levels']],
        'resistance_levels': [float(x) for x in position['resistance_levels']],
        
        # Explanations
        'reasons': position['reasons'],
        'technical_details': position['technical_details'],
        
        # Fear & Greed
        'fear_greed_value': position['fear_greed_value'],
        'fear_greed_classification': position['fear_greed_classification'],
        
        # Chart data (last 100 candles for performance)
        'chart_data': {
            'timestamps': [ts.isoformat() for ts in position['dataframe'].index[-100:]],
            'close': position['dataframe']['close'].iloc[-100:].tolist(),
            'high': position['dataframe']['high'].iloc[-100:].tolist(),
            'low': position['dataframe']['low'].iloc[-100:].tolist(),
            'volume': position['dataframe']['volume'].iloc[-100:].tolist(),
            'ema_12': position['analysis']['ema_12'].iloc[-100:].tolist(),
            'ema_26': position['analysis']['ema_26'].iloc[-100:].tolist(),
            'sma_50': position['analysis']['sma_50'].iloc[-100:].tolist(),
            'bb_upper': position['analysis']['bb_upper'].iloc[-100:].tolist(),
            'bb_lower': position['analysis']['bb_lower'].iloc[-100:].tolist(),
        }
    }
    
    return serialized


import pandas as pd


@app.get("/")
async def root():
    """API root endpoint - serves React frontend if available, otherwise API info"""
    # Check if frontend build exists
    frontend_build_path = Path(__file__).parent / "btc-trading-frontend" / "build"
    index_path = frontend_build_path / "index.html"
    
    if index_path.exists():
        # Serve React frontend
        from fastapi.responses import FileResponse
        return FileResponse(index_path)
    else:
        # Return API info if frontend not built
        return {
            "message": "BTC Trading System API",
            "version": "1.0.0",
            "endpoints": {
                "positions": "/api/positions",
                "fear_greed": "/api/fear-greed",
                "current_price": "/api/current-price",
                "websocket": "/ws"
            }
        }


@app.get("/api/positions")
async def get_positions():
    """Get all position suggestions for all timeframes"""
    try:
        logger.info("Fetching positions for all timeframes...")
        
        positions = analyzer.analyze_all_timeframes("BTCUSDT")
        
        # Serialize positions
        serialized_positions = [serialize_position(pos) for pos in positions]
        
        return JSONResponse(content={
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "positions": serialized_positions,
            "count": len(serialized_positions)
        })
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.get("/api/fear-greed")
async def get_fear_greed():
    """Get Fear & Greed Index"""
    try:
        fg_data = fear_greed_fetcher.fetch_current()
        
        return JSONResponse(content={
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "value": fg_data.value,
                "classification": fg_data.classification,
                "time_until_update": fg_data.time_until_update,
                "is_extreme_fear": fg_data.is_extreme_fear(),
                "is_extreme_greed": fg_data.is_extreme_greed(),
                "is_fear": fg_data.is_fear(),
                "is_greed": fg_data.is_greed(),
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching Fear & Greed: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.get("/api/current-price")
async def get_current_price():
    """Get current BTC price from multiple sources"""
    try:
        prices = data_fetcher.get_current_prices_from_all_sources("BTCUSDT")
        
        return JSONResponse(content={
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "prices": prices
        })
        
    except Exception as e:
        logger.error(f"Error fetching current price: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.get("/api/position/{timeframe}")
async def get_position_by_timeframe(timeframe: str):
    """Get position suggestion for specific timeframe"""
    try:
        positions = analyzer.analyze_all_timeframes("BTCUSDT")
        
        # Find the requested timeframe
        position = next((p for p in positions if p['timeframe'] == timeframe), None)
        
        if not position:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": f"Timeframe '{timeframe}' not found"}
            )
        
        return JSONResponse(content={
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "position": serialize_position(position)
        })
        
    except Exception as e:
        logger.error(f"Error fetching position for {timeframe}: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send updates every 60 seconds
            try:
                logger.info("Generating real-time update...")
                
                # Get fresh data
                positions = analyzer.analyze_all_timeframes("BTCUSDT")
                fg_data = fear_greed_fetcher.fetch_current()
                prices = data_fetcher.get_current_prices_from_all_sources("BTCUSDT")
                
                # Serialize and send
                update = {
                    "type": "update",
                    "timestamp": datetime.now().isoformat(),
                    "positions": [serialize_position(pos) for pos in positions],
                    "fear_greed": {
                        "value": fg_data.value,
                        "classification": fg_data.classification,
                    },
                    "current_price": prices.get('average', prices.get('binance', 0))
                }
                
                await manager.broadcast(update)
                
            except Exception as e:
                logger.error(f"Error in WebSocket update: {e}")
            
            # Wait 60 seconds before next update
            await asyncio.sleep(60)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections)
    }


# Serve React frontend static files (for production)
# Check if the build directory exists
frontend_build_path = Path(__file__).parent / "btc-trading-frontend" / "build"
if frontend_build_path.exists():
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
    
    # Serve index.html for all other routes (React Router support)
    from fastapi.responses import FileResponse
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for all non-API routes"""
        # Don't serve React app for API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        
        # Serve index.html for all other routes
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            return JSONResponse(
                status_code=503,
                content={"detail": "Frontend not built yet. Run: cd btc-trading-frontend && npm run build"}
            )
    
    logger.info("✅ Serving React frontend from /btc-trading-frontend/build")
else:
    logger.warning("⚠️  Frontend build directory not found. API-only mode.")
    logger.warning("   To enable frontend, run: cd btc-trading-frontend && npm run build")


if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("🚀 Starting BTC Trading System API")
    print("="*70)
    print("API Documentation: http://localhost:8123/docs")
    print("WebSocket: ws://localhost:8123/ws")
    print("="*70)
    
    uvicorn.run(app, host="0.0.0.0", port=8123, log_level="info")

