"""
Improved Real-Time Trading Engine
==================================
Enhanced trading engine with:
- Position tracking
- Fear & Greed Index integration
- Risk management
- Better error handling
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional
import logging

from config import SystemConfig
from enhanced_websocket import MultiStreamWebSocket
from fear_greed_index import FearGreedIndexFetcher, FearGreedSignalEnhancer, FearGreedData
from position_tracker import PositionTracker, Position

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators"""
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD"""
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram


class ImprovedTradingEngine:
    """
    Enhanced real-time trading engine with:
    - Multi-stream WebSocket
    - Position tracking
    - Fear & Greed Index integration
    - Risk management
    """
    
    def __init__(self, config: SystemConfig):
        self.config = config
        
        # Initialize components
        self.websocket = MultiStreamWebSocket(symbol=config.data.symbol)
        self.position_tracker = PositionTracker(initial_capital=config.risk.initial_capital)
        self.fear_greed_fetcher = FearGreedIndexFetcher()
        self.fear_greed_enhancer = FearGreedSignalEnhancer(self.fear_greed_fetcher)
        self.indicators_calc = TechnicalIndicators()
        
        # Data buffers
        self.price_buffer = pd.DataFrame()
        self.current_fear_greed: Optional[FearGreedData] = None
        
        # State
        self.is_running = False
        self.signal_count = 0
        
    async def start(self):
        """Start the trading engine"""
        logger.info("="*70)
        logger.info("🚀 IMPROVED TRADING ENGINE STARTING")
        logger.info("="*70)
        logger.info(f"Symbol: {self.config.data.symbol.upper()}")
        logger.info(f"Initial Capital: ${self.config.risk.initial_capital:,.2f}")
        logger.info(f"Fear & Greed Index: {'Enabled' if self.config.enable_fear_greed_index else 'Disabled'}")
        logger.info(f"Risk Management: {'Enabled' if self.config.enable_risk_management else 'Disabled'}")
        logger.info("="*70)
        
        self.is_running = True
        
        # Fetch initial Fear & Greed Index
        if self.config.enable_fear_greed_index:
            self.current_fear_greed = self.fear_greed_fetcher.fetch_current()
            if self.current_fear_greed:
                logger.info(f"😱 Fear & Greed Index: {self.current_fear_greed.value} "
                           f"({self.current_fear_greed.classification})")
        
        # Fetch historical data for indicators
        await self._load_historical_data()
        
        # Start WebSocket streams
        try:
            await self.websocket.start(
                trade_callback=self._on_trade_update,
                kline_callback=self._on_kline_update,
                fear_greed_callback=self._on_fear_greed_update if self.config.enable_fear_greed_index else None
            )
        except KeyboardInterrupt:
            await self.stop()
    
    async def _load_historical_data(self):
        """Load historical data for initial indicator calculation"""
        import requests
        
        logger.info("Loading historical data...")
        
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': self.config.data.symbol.upper(),
            'interval': '1m',
            'limit': 200
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df.set_index('timestamp', inplace=True)
            self.price_buffer = df[['open', 'high', 'low', 'close', 'volume']]
            
            logger.info(f"✅ Loaded {len(self.price_buffer)} historical candles")
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    async def _on_trade_update(self, trade_data: Dict):
        """Handle incoming trade updates"""
        try:
            # Add to buffer
            timestamp = trade_data['timestamp']
            price = trade_data['price']
            quantity = trade_data['quantity']
            
            # Create new row
            new_row = pd.DataFrame([{
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': quantity
            }], index=[timestamp])
            
            self.price_buffer = pd.concat([self.price_buffer, new_row])
            
            # Keep only recent data
            if len(self.price_buffer) > 500:
                self.price_buffer = self.price_buffer.tail(500)
            
            # Update open positions
            self.position_tracker.update_open_positions(price)
            
            # Check for signals every minute (when we have enough data)
            if len(self.price_buffer) > 100:
                # Resample to 1-minute candles
                df_resampled = self.price_buffer.resample('1min').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna()
                
                if len(df_resampled) > 50:
                    await self._check_for_signals(df_resampled)
            
        except Exception as e:
            logger.error(f"Error processing trade update: {e}")
    
    async def _on_kline_update(self, kline_data: Dict):
        """Handle kline (candlestick) updates"""
        if kline_data['is_closed']:
            logger.debug(f"Kline closed: ${kline_data['close']:,.2f}")
    
    async def _on_fear_greed_update(self, fear_greed_data: FearGreedData):
        """Handle Fear & Greed Index updates"""
        self.current_fear_greed = fear_greed_data
        logger.info(f"😱 Fear & Greed Index updated: {fear_greed_data.value} "
                   f"({fear_greed_data.classification})")
    
    async def _check_for_signals(self, df: pd.DataFrame):
        """Check for trading signals"""
        try:
            # Calculate indicators
            df = self._calculate_indicators(df)
            
            if len(df) < 2:
                return
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Check for BUY signal
            if len(self.position_tracker.open_positions) == 0:
                if self._is_buy_signal(latest, prev):
                    await self._execute_buy(latest)
            
            # Check for SELL signal
            elif len(self.position_tracker.open_positions) > 0:
                if self._is_sell_signal(latest, prev):
                    await self._execute_sell(latest)
            
        except Exception as e:
            logger.error(f"Error checking for signals: {e}")
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = df.copy()
        
        # EMAs
        df['ema_fast'] = self.indicators_calc.calculate_ema(
            df['close'], self.config.trading.ema_fast
        )
        df['ema_slow'] = self.indicators_calc.calculate_ema(
            df['close'], self.config.trading.ema_slow
        )
        
        # RSI
        df['rsi'] = self.indicators_calc.calculate_rsi(
            df['close'], self.config.trading.rsi_period
        )
        
        # MACD
        macd, signal, hist = self.indicators_calc.calculate_macd(
            df['close'],
            self.config.trading.macd_fast,
            self.config.trading.macd_slow,
            self.config.trading.macd_signal
        )
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_hist'] = hist
        
        return df
    
    def _is_buy_signal(self, latest: pd.Series, prev: pd.Series) -> bool:
        """Check if current conditions indicate a BUY signal"""
        # EMA crossover
        ema_cross_up = (prev['ema_fast'] <= prev['ema_slow'] and 
                       latest['ema_fast'] > latest['ema_slow'])
        
        # RSI conditions
        rsi_ok = latest['rsi'] < self.config.trading.rsi_overbought
        
        # MACD bullish
        macd_bullish = latest['macd'] > latest['macd_signal']
        
        base_signal = ema_cross_up and rsi_ok and macd_bullish
        
        # Enhance with Fear & Greed if enabled
        if self.config.enable_fear_greed_index and self.current_fear_greed:
            enhance, reason = self.fear_greed_enhancer.should_enhance_buy(self.current_fear_greed)
            if base_signal and enhance:
                logger.info(f"✨ Signal enhanced by Fear & Greed: {reason}")
                return True
            elif base_signal:
                logger.info(f"⚠️  Signal but not enhanced: {reason}")
                # Still allow the trade but with lower confidence
                return True
        
        return base_signal
    
    def _is_sell_signal(self, latest: pd.Series, prev: pd.Series) -> bool:
        """Check if current conditions indicate a SELL signal"""
        # EMA crossover
        ema_cross_down = (prev['ema_fast'] >= prev['ema_slow'] and 
                         latest['ema_fast'] < latest['ema_slow'])
        
        # RSI overbought
        rsi_overbought = latest['rsi'] > self.config.trading.rsi_exit
        
        # MACD bearish
        macd_bearish = latest['macd'] < latest['macd_signal']
        
        return ema_cross_down or rsi_overbought or macd_bearish
    
    async def _execute_buy(self, latest: pd.Series):
        """Execute a BUY order"""
        try:
            price = latest['close']
            
            # Calculate position size (simple: use % of capital)
            position_value = self.position_tracker.current_capital * 0.95  # 95% of capital
            position_size = position_value / price
            
            # Calculate stop loss and take profit
            stop_loss_price = price * (1 - 0.02)  # 2% stop loss
            take_profit_price = price * (1 + 0.04)  # 4% take profit
            
            # Get Fear & Greed confidence
            confidence = 1.0
            fear_greed_value = None
            if self.current_fear_greed:
                confidence = self.fear_greed_enhancer.get_signal_confidence('BUY', self.current_fear_greed)
                fear_greed_value = self.current_fear_greed.value
            
            # Build entry reason
            entry_reason = f"EMA crossover, RSI={latest['rsi']:.2f}, MACD={latest['macd']:.2f}"
            if self.current_fear_greed:
                entry_reason += f", F&G={self.current_fear_greed.value} ({self.current_fear_greed.classification})"
            
            # Open position
            position = self.position_tracker.open_position(
                entry_price=price,
                position_size=position_size,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                trailing_stop_pct=self.config.risk.trailing_stop_pct if self.config.risk.use_trailing_stop else 0,
                entry_reason=entry_reason,
                signal_confidence=confidence,
                fear_greed_value=fear_greed_value
            )
            
            if position:
                self.signal_count += 1
                logger.info(f"📊 Total signals generated: {self.signal_count}")
            
        except Exception as e:
            logger.error(f"Error executing BUY: {e}")
    
    async def _execute_sell(self, latest: pd.Series):
        """Execute a SELL order (close position)"""
        try:
            price = latest['close']
            
            # Close all open positions
            for position in self.position_tracker.open_positions.copy():
                exit_reason = f"EMA cross down or RSI overbought ({latest['rsi']:.2f})"
                self.position_tracker.close_position(position, price, exit_reason)
            
        except Exception as e:
            logger.error(f"Error executing SELL: {e}")
    
    async def stop(self):
        """Stop the trading engine"""
        logger.info("\n" + "="*70)
        logger.info("🛑 STOPPING TRADING ENGINE")
        logger.info("="*70)
        
        self.is_running = False
        
        # Close all open positions
        if self.price_buffer is not None and len(self.price_buffer) > 0:
            last_price = self.price_buffer['close'].iloc[-1]
            self.position_tracker.close_all_positions(last_price, "Engine shutdown")
        
        # Stop WebSocket
        await self.websocket.stop()
        
        # Print summary
        self.position_tracker.print_summary()
        
        # Save positions to file
        self.position_tracker.save_to_file()
        
        logger.info("="*70)
        logger.info("👋 Engine stopped successfully")
        logger.info("="*70)


# Example usage
async def main():
    """Main entry point"""
    from config import SystemConfig, TradingConfig, RiskConfig, DataConfig
    
    # Create configuration
    config = SystemConfig(
        trading=TradingConfig(
            ema_fast=20,
            ema_slow=50,
            rsi_period=14,
            rsi_overbought=70,
            rsi_exit=80
        ),
        risk=RiskConfig(
            initial_capital=10000.0,
            max_risk_per_trade_pct=2.0,
            use_trailing_stop=True,
            trailing_stop_pct=2.0
        ),
        data=DataConfig(
            symbol="btcusdt"
        ),
        enable_fear_greed_index=True,
        enable_risk_management=True
    )
    
    # Create and start engine
    engine = ImprovedTradingEngine(config)
    
    try:
        await engine.start()
    except KeyboardInterrupt:
        await engine.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("🚀 IMPROVED BITCOIN TRADING ENGINE")
    print("="*70)
    print("Features:")
    print("  ✅ Real-time WebSocket streaming")
    print("  ✅ Fear & Greed Index integration")
    print("  ✅ Position tracking")
    print("  ✅ Risk management")
    print("  ✅ Automatic stop-loss and take-profit")
    print("="*70)
    print("\nPress Ctrl+C to stop\n")
    
    asyncio.run(main())

