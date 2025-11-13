"""
Enhanced WebSocket Module
==========================
Improved WebSocket with auto-reconnection, error handling, and multi-source streaming
"""

import asyncio
import json
import websockets
from datetime import datetime
from typing import Dict, Optional, Callable
import logging
from dataclasses import dataclass
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class StreamConfig:
    """WebSocket stream configuration"""
    symbol: str = "btcusdt"
    max_reconnect_attempts: int = 10
    reconnect_delay: int = 5
    heartbeat_interval: int = 30
    connection_timeout: int = 10


class EnhancedBinanceWebSocket:
    """
    Enhanced Binance WebSocket with:
    - Automatic reconnection
    - Connection health monitoring
    - Error recovery
    - Multi-stream support
    """
    
    def __init__(self, config: StreamConfig):
        self.config = config
        self.ws_url = f"wss://stream.binance.com:9443/ws/{config.symbol.lower()}@trade"
        self.kline_url = f"wss://stream.binance.com:9443/ws/{config.symbol.lower()}@kline_1m"
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_running = False
        self.reconnect_count = 0
        self.last_message_time: Optional[datetime] = None
        self.message_count = 0
        
        # Connection statistics
        self.connection_start_time: Optional[datetime] = None
        self.total_messages_received = 0
        self.total_reconnections = 0
        
    async def connect(self, callback: Callable):
        """
        Connect to Binance WebSocket with auto-reconnection
        
        Args:
            callback: Async function to call with each trade update
        """
        self.is_running = True
        
        while self.is_running:
            try:
                logger.info(f"Connecting to Binance WebSocket: {self.config.symbol.upper()}")
                
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=10
                ) as websocket:
                    self.websocket = websocket
                    self.connection_start_time = datetime.now()
                    self.reconnect_count = 0
                    
                    logger.info("✅ Connected successfully!")
                    
                    # Start heartbeat monitor
                    heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
                    
                    try:
                        async for message in websocket:
                            if not self.is_running:
                                break
                            
                            await self._process_message(message, callback)
                            
                    finally:
                        heartbeat_task.cancel()
                        
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"Connection closed: {e}")
                await self._handle_reconnection()
                
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await self._handle_reconnection()
    
    async def _process_message(self, message: str, callback: Callable):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            self.last_message_time = datetime.now()
            self.message_count += 1
            self.total_messages_received += 1
            
            # Parse trade data
            trade_data = {
                'timestamp': datetime.fromtimestamp(data['T'] / 1000),
                'price': float(data['p']),
                'quantity': float(data['q']),
                'symbol': data['s'],
                'is_buyer_maker': data['m']
            }
            
            # Log every 100 messages
            if self.message_count % 100 == 0:
                logger.info(f"📊 Processed {self.message_count} messages | "
                          f"Latest price: ${trade_data['price']:,.2f}")
            
            # Call the callback
            await callback(trade_data)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _heartbeat_monitor(self):
        """Monitor connection health"""
        while self.is_running:
            await asyncio.sleep(self.config.heartbeat_interval)
            
            if self.last_message_time:
                elapsed = (datetime.now() - self.last_message_time).total_seconds()
                if elapsed > self.config.heartbeat_interval * 2:
                    logger.warning(f"⚠️  No messages received for {elapsed:.0f}s")
                else:
                    logger.debug(f"❤️  Connection healthy (last message {elapsed:.0f}s ago)")
    
    async def _handle_reconnection(self):
        """Handle reconnection logic"""
        self.reconnect_count += 1
        self.total_reconnections += 1
        
        if self.reconnect_count >= self.config.max_reconnect_attempts:
            logger.error(f"❌ Max reconnection attempts ({self.config.max_reconnect_attempts}) reached")
            self.is_running = False
            return
        
        logger.info(f"🔄 Reconnecting in {self.config.reconnect_delay}s "
                   f"(Attempt {self.reconnect_count}/{self.config.max_reconnect_attempts})")
        
        await asyncio.sleep(self.config.reconnect_delay)
    
    async def disconnect(self):
        """Gracefully disconnect"""
        logger.info("Disconnecting WebSocket...")
        self.is_running = False
        
        if self.websocket:
            await self.websocket.close()
        
        logger.info("Disconnected")
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        uptime = None
        if self.connection_start_time:
            uptime = (datetime.now() - self.connection_start_time).total_seconds()
        
        return {
            'is_connected': self.is_running and self.websocket is not None,
            'total_messages': self.total_messages_received,
            'total_reconnections': self.total_reconnections,
            'uptime_seconds': uptime,
            'last_message_time': self.last_message_time
        }


class MultiStreamWebSocket:
    """
    Manage multiple WebSocket streams simultaneously
    - Binance trades
    - Binance klines
    - Fear & Greed Index updates
    """
    
    def __init__(self, symbol: str = "btcusdt"):
        self.symbol = symbol.lower()
        self.binance_ws: Optional[EnhancedBinanceWebSocket] = None
        self.fear_greed_task: Optional[asyncio.Task] = None
        
        # Data callbacks
        self.trade_callback: Optional[Callable] = None
        self.kline_callback: Optional[Callable] = None
        self.fear_greed_callback: Optional[Callable] = None
        
        self.is_running = False
    
    async def start(self,
                   trade_callback: Optional[Callable] = None,
                   kline_callback: Optional[Callable] = None,
                   fear_greed_callback: Optional[Callable] = None):
        """
        Start all WebSocket streams
        
        Args:
            trade_callback: Function to call with trade updates
            kline_callback: Function to call with kline updates
            fear_greed_callback: Function to call with Fear & Greed updates
        """
        self.is_running = True
        self.trade_callback = trade_callback
        self.kline_callback = kline_callback
        self.fear_greed_callback = fear_greed_callback
        
        tasks = []
        
        # Start Binance trade stream
        if trade_callback:
            config = StreamConfig(symbol=self.symbol)
            self.binance_ws = EnhancedBinanceWebSocket(config)
            tasks.append(asyncio.create_task(
                self.binance_ws.connect(trade_callback)
            ))
        
        # Start kline stream
        if kline_callback:
            tasks.append(asyncio.create_task(
                self._kline_stream()
            ))
        
        # Start Fear & Greed Index stream
        if fear_greed_callback:
            tasks.append(asyncio.create_task(
                self._fear_greed_stream()
            ))
        
        logger.info(f"Started {len(tasks)} WebSocket streams")
        
        # Wait for all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _kline_stream(self):
        """Stream kline (candlestick) data"""
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_1m"
        
        while self.is_running:
            try:
                async with websockets.connect(url) as websocket:
                    logger.info("📊 Kline stream connected")
                    
                    async for message in websocket:
                        if not self.is_running:
                            break
                        
                        data = json.loads(message)
                        kline = data['k']
                        
                        kline_data = {
                            'timestamp': datetime.fromtimestamp(kline['t'] / 1000),
                            'open': float(kline['o']),
                            'high': float(kline['h']),
                            'low': float(kline['l']),
                            'close': float(kline['c']),
                            'volume': float(kline['v']),
                            'is_closed': kline['x']
                        }
                        
                        if self.kline_callback:
                            await self.kline_callback(kline_data)
                        
            except Exception as e:
                logger.error(f"Kline stream error: {e}")
                await asyncio.sleep(5)
    
    async def _fear_greed_stream(self):
        """Stream Fear & Greed Index updates"""
        from fear_greed_index import FearGreedIndexFetcher
        
        fetcher = FearGreedIndexFetcher()
        
        logger.info("😱 Fear & Greed Index stream started (updates every hour)")
        
        while self.is_running:
            try:
                # Fetch current index
                data = fetcher.fetch_current()
                
                if data and self.fear_greed_callback:
                    await self.fear_greed_callback(data)
                
                # Update every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Fear & Greed stream error: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop all streams"""
        logger.info("Stopping all WebSocket streams...")
        self.is_running = False
        
        if self.binance_ws:
            await self.binance_ws.disconnect()
        
        logger.info("All streams stopped")


# Example usage
async def example_multi_stream():
    """Example of using multi-stream WebSocket"""
    
    async def on_trade(trade_data):
        logger.info(f"Trade: ${trade_data['price']:,.2f} | {trade_data['quantity']:.6f} BTC")
    
    async def on_kline(kline_data):
        if kline_data['is_closed']:
            logger.info(f"Kline closed: O:{kline_data['open']:,.2f} "
                       f"H:{kline_data['high']:,.2f} "
                       f"L:{kline_data['low']:,.2f} "
                       f"C:{kline_data['close']:,.2f}")
    
    async def on_fear_greed(fg_data):
        logger.info(f"Fear & Greed Index: {fg_data.value} ({fg_data.classification})")
    
    stream = MultiStreamWebSocket(symbol="btcusdt")
    
    try:
        await stream.start(
            trade_callback=on_trade,
            kline_callback=on_kline,
            fear_greed_callback=on_fear_greed
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await stream.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("="*70)
    print("ENHANCED WEBSOCKET DEMO")
    print("="*70)
    print("Press Ctrl+C to stop\n")
    
    asyncio.run(example_multi_stream())

