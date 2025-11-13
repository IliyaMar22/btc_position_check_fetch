"""
Advanced Technical Analysis Module
===================================
Comprehensive technical indicators including:
- Moving Averages (SMA, EMA, WMA)
- RSI, MACD, Stochastic
- Bollinger Bands
- Fibonacci Retracement & Extensions
- Support & Resistance Levels
- Volume Analysis
- Trend Detection
- Pattern Recognition
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.signal import argrelextrema
import logging

logger = logging.getLogger(__name__)


class AdvancedTechnicalAnalysis:
    """Comprehensive technical analysis toolkit"""
    
    def __init__(self):
        self.support_resistance_window = 20
        
    # ============================================================================
    # MOVING AVERAGES
    # ============================================================================
    
    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    def calculate_wma(self, data: pd.Series, period: int) -> pd.Series:
        """Weighted Moving Average"""
        weights = np.arange(1, period + 1)
        return data.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Volume Weighted Average Price"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    
    # ============================================================================
    # MOMENTUM INDICATORS
    # ============================================================================
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_stochastic(self, df: pd.DataFrame, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Stochastic Oscillator"""
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        
        k = 100 * (df['close'] - low_min) / (high_max - low_min)
        k = k.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()
        
        return k, d
    
    def calculate_momentum(self, data: pd.Series, period: int = 10) -> pd.Series:
        """Momentum Indicator"""
        return data.diff(period)
    
    def calculate_roc(self, data: pd.Series, period: int = 12) -> pd.Series:
        """Rate of Change"""
        return ((data - data.shift(period)) / data.shift(period)) * 100
    
    # ============================================================================
    # VOLATILITY INDICATORS
    # ============================================================================
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        middle_band = self.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        return upper_band, middle_band, lower_band
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(period).mean()
        
        return atr
    
    def calculate_keltner_channels(self, df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Keltner Channels"""
        middle_line = self.calculate_ema(df['close'], period)
        atr = self.calculate_atr(df, period)
        upper_channel = middle_line + (multiplier * atr)
        lower_channel = middle_line - (multiplier * atr)
        return upper_channel, middle_line, lower_channel
    
    # ============================================================================
    # FIBONACCI LEVELS
    # ============================================================================
    
    def calculate_fibonacci_retracement(self, high: float, low: float) -> Dict[str, float]:
        """
        Calculate Fibonacci Retracement Levels
        
        Returns levels for downtrend (from high to low)
        """
        diff = high - low
        
        levels = {
            'level_0': high,
            'level_236': high - (0.236 * diff),
            'level_382': high - (0.382 * diff),
            'level_500': high - (0.500 * diff),
            'level_618': high - (0.618 * diff),
            'level_786': high - (0.786 * diff),
            'level_100': low
        }
        
        return levels
    
    def calculate_fibonacci_extension(self, high: float, low: float, retracement: float) -> Dict[str, float]:
        """
        Calculate Fibonacci Extension Levels
        
        Used for profit targets
        """
        diff = high - low
        
        levels = {
            'extension_1272': retracement + (1.272 * diff),
            'extension_1414': retracement + (1.414 * diff),
            'extension_1618': retracement + (1.618 * diff),
            'extension_2000': retracement + (2.000 * diff),
            'extension_2618': retracement + (2.618 * diff)
        }
        
        return levels
    
    def find_swing_high_low(self, df: pd.DataFrame, order: int = 5) -> Tuple[pd.Series, pd.Series]:
        """
        Find swing highs and lows for Fibonacci analysis
        
        Args:
            order: Number of candles on each side to compare
        """
        # Find local maxima (swing highs)
        highs = df['high'].values
        swing_highs_idx = argrelextrema(highs, np.greater, order=order)[0]
        
        # Find local minima (swing lows)
        lows = df['low'].values
        swing_lows_idx = argrelextrema(lows, np.less, order=order)[0]
        
        swing_highs = pd.Series(index=df.index, dtype=float)
        swing_highs.iloc[swing_highs_idx] = highs[swing_highs_idx]
        
        swing_lows = pd.Series(index=df.index, dtype=float)
        swing_lows.iloc[swing_lows_idx] = lows[swing_lows_idx]
        
        return swing_highs, swing_lows
    
    # ============================================================================
    # SUPPORT & RESISTANCE
    # ============================================================================
    
    def find_support_resistance(self, df: pd.DataFrame, window: int = 20, num_levels: int = 5) -> Dict[str, List[float]]:
        """
        Identify Support and Resistance Levels
        
        Uses local minima/maxima and clustering
        """
        # Find swing highs and lows
        swing_highs, swing_lows = self.find_swing_high_low(df, order=window//4)
        
        # Get resistance levels (from swing highs)
        resistance_prices = swing_highs.dropna().values
        
        # Get support levels (from swing lows)
        support_prices = swing_lows.dropna().values
        
        # Cluster nearby levels
        resistance_levels = self._cluster_levels(resistance_prices, num_levels)
        support_levels = self._cluster_levels(support_prices, num_levels)
        
        return {
            'resistance': sorted(resistance_levels, reverse=True),
            'support': sorted(support_levels),
            'all_swing_highs': resistance_prices.tolist(),
            'all_swing_lows': support_prices.tolist()
        }
    
    def _cluster_levels(self, prices: np.ndarray, num_clusters: int) -> List[float]:
        """Cluster similar price levels together"""
        if len(prices) == 0:
            return []
        
        # Simple clustering by grouping nearby prices
        sorted_prices = np.sort(prices)
        clusters = []
        current_cluster = [sorted_prices[0]]
        
        threshold = np.std(prices) * 0.5  # 0.5 standard deviations
        
        for price in sorted_prices[1:]:
            if price - current_cluster[-1] <= threshold:
                current_cluster.append(price)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [price]
        
        clusters.append(np.mean(current_cluster))
        
        # Return top N clusters
        return sorted(clusters, reverse=True)[:num_clusters]
    
    def check_breakout(self, current_price: float, support_resistance: Dict) -> Dict[str, bool]:
        """Check if price has broken through support or resistance"""
        resistance_levels = support_resistance['resistance']
        support_levels = support_resistance['support']
        
        # Check resistance breakout
        resistance_breakout = False
        if resistance_levels:
            nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
            if current_price > nearest_resistance:
                resistance_breakout = True
        
        # Check support breakdown
        support_breakdown = False
        if support_levels:
            nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
            if current_price < nearest_support:
                support_breakdown = True
        
        return {
            'resistance_breakout': resistance_breakout,
            'support_breakdown': support_breakdown,
            'nearest_resistance': nearest_resistance if resistance_levels else None,
            'nearest_support': nearest_support if support_levels else None
        }
    
    # ============================================================================
    # VOLUME ANALYSIS
    # ============================================================================
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """On-Balance Volume"""
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        return obv
    
    def calculate_volume_sma(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Volume Simple Moving Average"""
        return df['volume'].rolling(window=period).mean()
    
    def volume_breakout(self, df: pd.DataFrame, threshold: float = 1.5) -> pd.Series:
        """Detect volume breakouts (volume > threshold * average)"""
        avg_volume = self.calculate_volume_sma(df, 20)
        return df['volume'] > (avg_volume * threshold)
    
    def calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Money Flow Index (Volume-weighted RSI)"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        
        positive_mf = positive_flow.rolling(period).sum()
        negative_mf = negative_flow.rolling(period).sum()
        
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        
        return mfi
    
    # ============================================================================
    # TREND DETECTION
    # ============================================================================
    
    def detect_trend(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Detect trend direction
        
        Returns: 1 (uptrend), 0 (sideways), -1 (downtrend)
        """
        sma = self.calculate_sma(df['close'], period)
        
        trend = pd.Series(index=df.index, dtype=int)
        trend[df['close'] > sma] = 1   # Uptrend
        trend[df['close'] < sma] = -1  # Downtrend
        trend[df['close'] == sma] = 0  # Sideways
        
        return trend
    
    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Average Directional Index (Trend Strength)
        
        Returns: ADX, +DI, -DI
        """
        # Calculate True Range
        tr = self.calculate_atr(df, 1) * 1  # Single period TR
        
        # Calculate Directional Movement
        up_move = df['high'].diff()
        down_move = -df['low'].diff()
        
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        
        # Smooth the values
        atr = self.calculate_atr(df, period)
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        
        # Calculate ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        
        return adx, plus_di, minus_di
    
    # ============================================================================
    # PATTERN RECOGNITION
    # ============================================================================
    
    def detect_candlestick_patterns(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Detect common candlestick patterns
        """
        patterns = {}
        
        # Doji
        body = abs(df['close'] - df['open'])
        range_size = df['high'] - df['low']
        patterns['doji'] = body < (range_size * 0.1)
        
        # Hammer / Hanging Man
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        patterns['hammer'] = (lower_shadow > body * 2) & (upper_shadow < body * 0.3)
        
        # Engulfing
        bullish_engulfing = (
            (df['close'].shift(1) < df['open'].shift(1)) &  # Previous candle bearish
            (df['close'] > df['open']) &                     # Current candle bullish
            (df['open'] < df['close'].shift(1)) &            # Opens below previous close
            (df['close'] > df['open'].shift(1))              # Closes above previous open
        )
        patterns['bullish_engulfing'] = bullish_engulfing
        
        bearish_engulfing = (
            (df['close'].shift(1) > df['open'].shift(1)) &  # Previous candle bullish
            (df['close'] < df['open']) &                     # Current candle bearish
            (df['open'] > df['close'].shift(1)) &            # Opens above previous close
            (df['close'] < df['open'].shift(1))              # Closes below previous open
        )
        patterns['bearish_engulfing'] = bearish_engulfing
        
        return patterns
    
    # ============================================================================
    # COMPREHENSIVE ANALYSIS
    # ============================================================================
    
    def analyze_all(self, df: pd.DataFrame) -> Dict:
        """
        Run comprehensive technical analysis
        
        Returns all indicators and analysis
        """
        logger.info("Running comprehensive technical analysis...")
        
        analysis = {}
        
        # Moving Averages
        analysis['sma_20'] = self.calculate_sma(df['close'], 20)
        analysis['sma_50'] = self.calculate_sma(df['close'], 50)
        analysis['sma_200'] = self.calculate_sma(df['close'], 200)
        analysis['ema_12'] = self.calculate_ema(df['close'], 12)
        analysis['ema_26'] = self.calculate_ema(df['close'], 26)
        
        # Momentum
        analysis['rsi'] = self.calculate_rsi(df['close'])
        macd, signal, hist = self.calculate_macd(df['close'])
        analysis['macd'] = macd
        analysis['macd_signal'] = signal
        analysis['macd_hist'] = hist
        
        stoch_k, stoch_d = self.calculate_stochastic(df)
        analysis['stoch_k'] = stoch_k
        analysis['stoch_d'] = stoch_d
        
        # Volatility
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(df['close'])
        analysis['bb_upper'] = bb_upper
        analysis['bb_middle'] = bb_middle
        analysis['bb_lower'] = bb_lower
        analysis['atr'] = self.calculate_atr(df)
        
        # Volume
        analysis['obv'] = self.calculate_obv(df)
        analysis['volume_sma'] = self.calculate_volume_sma(df)
        analysis['mfi'] = self.calculate_mfi(df)
        
        # Trend
        analysis['trend'] = self.detect_trend(df)
        adx, plus_di, minus_di = self.calculate_adx(df)
        analysis['adx'] = adx
        analysis['plus_di'] = plus_di
        analysis['minus_di'] = minus_di
        
        # Support & Resistance
        support_resistance = self.find_support_resistance(df)
        analysis['support_levels'] = support_resistance['support']
        analysis['resistance_levels'] = support_resistance['resistance']
        
        # Fibonacci (recent swing)
        if len(df) >= 50:
            recent_high = df['high'].tail(50).max()
            recent_low = df['low'].tail(50).min()
            fib_levels = self.calculate_fibonacci_retracement(recent_high, recent_low)
            analysis['fibonacci_levels'] = fib_levels
        
        # Patterns
        patterns = self.detect_candlestick_patterns(df)
        analysis['patterns'] = patterns
        
        logger.info("✅ Technical analysis complete!")
        
        return analysis


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("ADVANCED TECHNICAL ANALYSIS - DEMO")
    print("="*70)
    
    # Create sample data
    from multi_source_data_fetcher import MultiSourceDataAggregator
    
    aggregator = MultiSourceDataAggregator()
    df = aggregator.get_comprehensive_data("BTCUSDT", "1h", days=30)
    
    if not df.empty:
        ta = AdvancedTechnicalAnalysis()
        
        # Run comprehensive analysis
        analysis = ta.analyze_all(df)
        
        # Display latest values
        print("\n📊 LATEST TECHNICAL INDICATORS")
        print("="*70)
        
        current_price = df['close'].iloc[-1]
        print(f"\nCurrent Price: ${current_price:,.2f}")
        
        print(f"\n📈 Moving Averages:")
        print(f"  SMA 20: ${analysis['sma_20'].iloc[-1]:,.2f}")
        print(f"  SMA 50: ${analysis['sma_50'].iloc[-1]:,.2f}")
        print(f"  SMA 200: ${analysis['sma_200'].iloc[-1]:,.2f}")
        
        print(f"\n💪 Momentum:")
        print(f"  RSI: {analysis['rsi'].iloc[-1]:.2f}")
        print(f"  MACD: {analysis['macd'].iloc[-1]:.2f}")
        print(f"  Stochastic %K: {analysis['stoch_k'].iloc[-1]:.2f}")
        
        print(f"\n📊 Volatility:")
        print(f"  BB Upper: ${analysis['bb_upper'].iloc[-1]:,.2f}")
        print(f"  BB Lower: ${analysis['bb_lower'].iloc[-1]:,.2f}")
        print(f"  ATR: ${analysis['atr'].iloc[-1]:,.2f}")
        
        print(f"\n📈 Trend:")
        trend = analysis['trend'].iloc[-1]
        trend_text = "UPTREND" if trend == 1 else "DOWNTREND" if trend == -1 else "SIDEWAYS"
        print(f"  Trend: {trend_text}")
        print(f"  ADX: {analysis['adx'].iloc[-1]:.2f}")
        
        print(f"\n🎯 Support & Resistance:")
        print(f"  Resistance: {[f'${x:,.2f}' for x in analysis['resistance_levels'][:3]]}")
        print(f"  Support: {[f'${x:,.2f}' for x in analysis['support_levels'][:3]]}")
        
        if 'fibonacci_levels' in analysis:
            print(f"\n📐 Fibonacci Levels:")
            for level, price in analysis['fibonacci_levels'].items():
                print(f"  {level}: ${price:,.2f}")
        
        print("\n" + "="*70)

