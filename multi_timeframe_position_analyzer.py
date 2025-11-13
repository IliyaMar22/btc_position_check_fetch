"""
Multi-Timeframe Position Analyzer
==================================
Analyzes Bitcoin across multiple timeframes and provides detailed position suggestions:
- 15 min, 1 hour, 4 hours, 1 day, 1 week
- Comprehensive technical analysis for each
- Visual charts with entry/exit markers
- Detailed explanations with supporting evidence
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

from multi_source_data_fetcher import MultiSourceDataAggregator
from advanced_technical_analysis import AdvancedTechnicalAnalysis
from fear_greed_index import FearGreedIndexFetcher, FearGreedSignalEnhancer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiTimeframePositionAnalyzer:
    """Analyze positions across multiple timeframes with detailed explanations"""
    
    def __init__(self):
        self.data_fetcher = MultiSourceDataAggregator()
        self.technical_analysis = AdvancedTechnicalAnalysis()
        self.fear_greed = FearGreedIndexFetcher()
        
        # Timeframe configurations
        self.timeframes = {
            '15m': {'interval': '15m', 'days': 7, 'name': '15 Minutes'},
            '1h': {'interval': '1h', 'days': 14, 'name': '1 Hour'},
            '4h': {'interval': '4h', 'days': 30, 'name': '4 Hours'},
            '1d': {'interval': '1d', 'days': 90, 'name': '1 Day'},
            '1w': {'interval': '1w', 'days': 365, 'name': '1 Week'}
        }
        
    def analyze_all_timeframes(self, symbol: str = "BTCUSDT") -> List[Dict]:
        """
        Analyze all timeframes and generate position suggestions
        
        Returns:
            List of position suggestions with detailed analysis
        """
        logger.info(f"🔍 Analyzing {symbol} across {len(self.timeframes)} timeframes...")
        
        # Get current prices
        prices = self.data_fetcher.get_current_prices_from_all_sources(symbol)
        current_price = prices.get('average', prices.get('binance', 0))
        
        # Get Fear & Greed
        fg_data = self.fear_greed.fetch_current()
        fg_enhancer = FearGreedSignalEnhancer(self.fear_greed)
        
        positions = []
        
        for tf_key, tf_config in self.timeframes.items():
            logger.info(f"\n📊 Analyzing {tf_config['name']} timeframe...")
            
            try:
                # Fetch data for this timeframe
                df = self.data_fetcher.get_comprehensive_data(
                    symbol=symbol,
                    interval=tf_config['interval'],
                    days=tf_config['days'],
                    sources=['binance']
                )
                
                if df.empty:
                    logger.warning(f"No data for {tf_key}, skipping...")
                    continue
                
                # Run technical analysis
                analysis = self.technical_analysis.analyze_all(df)
                
                # Generate position suggestion
                position = self._generate_position_suggestion(
                    timeframe=tf_key,
                    timeframe_name=tf_config['name'],
                    df=df,
                    analysis=analysis,
                    current_price=current_price,
                    fg_data=fg_data,
                    fg_enhancer=fg_enhancer
                )
                
                positions.append(position)
                
            except Exception as e:
                logger.error(f"Error analyzing {tf_key}: {e}")
                continue
        
        return positions
    
    def _generate_position_suggestion(self, 
                                     timeframe: str,
                                     timeframe_name: str,
                                     df: pd.DataFrame,
                                     analysis: Dict,
                                     current_price: float,
                                     fg_data,
                                     fg_enhancer) -> Dict:
        """Generate detailed position suggestion for a timeframe"""
        
        # Get latest values
        latest_idx = -1
        
        # Price action
        price_change_pct = ((df['close'].iloc[latest_idx] - df['close'].iloc[-10]) / df['close'].iloc[-10]) * 100
        
        # Moving averages
        ema_12 = analysis['ema_12'].iloc[latest_idx]
        ema_26 = analysis['ema_26'].iloc[latest_idx]
        sma_50 = analysis['sma_50'].iloc[latest_idx]
        sma_200 = analysis['sma_200'].iloc[latest_idx]
        
        # Momentum indicators
        rsi = analysis['rsi'].iloc[latest_idx]
        macd = analysis['macd'].iloc[latest_idx]
        macd_signal = analysis['macd_signal'].iloc[latest_idx]
        stoch_k = analysis['stoch_k'].iloc[latest_idx]
        
        # Volatility
        bb_upper = analysis['bb_upper'].iloc[latest_idx]
        bb_lower = analysis['bb_lower'].iloc[latest_idx]
        bb_middle = analysis['bb_middle'].iloc[latest_idx]
        atr = analysis['atr'].iloc[latest_idx]
        
        # Trend
        trend = analysis['trend'].iloc[latest_idx]
        adx = analysis['adx'].iloc[latest_idx]
        
        # Support/Resistance
        support_levels = analysis.get('support_levels', [])
        resistance_levels = analysis.get('resistance_levels', [])
        
        # Volume
        obv = analysis['obv'].iloc[latest_idx]
        volume_sma = analysis['volume_sma'].iloc[latest_idx]
        current_volume = df['volume'].iloc[latest_idx]
        
        # Fibonacci
        fib_levels = analysis.get('fibonacci_levels', {})
        
        # ========================================
        # SIGNAL CALCULATION
        # ========================================
        
        score = 0
        reasons = []
        technical_details = []
        
        # 1. TREND ANALYSIS
        if trend == 1:
            score += 2
            reasons.append("✅ Bullish trend confirmed")
            technical_details.append(f"Price above EMA 12 ({ema_12:.2f}) and EMA 26 ({ema_26:.2f})")
        elif trend == -1:
            score -= 2
            reasons.append("❌ Bearish trend confirmed")
            technical_details.append(f"Price below EMA 12 ({ema_12:.2f}) and EMA 26 ({ema_26:.2f})")
        
        # Golden/Death Cross
        if current_price > sma_50 > sma_200:
            score += 1
            reasons.append("✅ Golden Cross formation (bullish)")
            technical_details.append(f"SMA 50 ({sma_50:.2f}) > SMA 200 ({sma_200:.2f})")
        elif current_price < sma_50 < sma_200:
            score -= 1
            reasons.append("❌ Death Cross formation (bearish)")
            technical_details.append(f"SMA 50 ({sma_50:.2f}) < SMA 200 ({sma_200:.2f})")
        
        # 2. MOMENTUM ANALYSIS
        if rsi < 30:
            score += 3
            reasons.append("✅✅✅ RSI OVERSOLD - Strong buy signal")
            technical_details.append(f"RSI at {rsi:.2f} (< 30 = oversold)")
        elif 30 <= rsi < 40:
            score += 2
            reasons.append("✅✅ RSI approaching oversold")
            technical_details.append(f"RSI at {rsi:.2f} (healthy for entry)")
        elif 40 <= rsi <= 60:
            score += 1
            reasons.append("✅ RSI neutral (healthy)")
            technical_details.append(f"RSI at {rsi:.2f} (balanced momentum)")
        elif 60 < rsi <= 70:
            score -= 1
            reasons.append("⚠️  RSI approaching overbought")
            technical_details.append(f"RSI at {rsi:.2f} (caution)")
        elif rsi > 70:
            score -= 3
            reasons.append("❌❌❌ RSI OVERBOUGHT - Sell signal")
            technical_details.append(f"RSI at {rsi:.2f} (> 70 = overbought)")
        
        # MACD
        if macd > macd_signal and macd > 0:
            score += 2
            reasons.append("✅✅ MACD bullish crossover")
            technical_details.append(f"MACD ({macd:.2f}) > Signal ({macd_signal:.2f})")
        elif macd > macd_signal:
            score += 1
            reasons.append("✅ MACD turning bullish")
            technical_details.append(f"MACD ({macd:.2f}) crossing above signal")
        elif macd < macd_signal and macd < 0:
            score -= 2
            reasons.append("❌❌ MACD bearish crossover")
            technical_details.append(f"MACD ({macd:.2f}) < Signal ({macd_signal:.2f})")
        
        # Stochastic
        if stoch_k < 20:
            score += 1
            reasons.append("✅ Stochastic oversold")
            technical_details.append(f"Stochastic K at {stoch_k:.2f} (< 20)")
        elif stoch_k > 80:
            score -= 1
            reasons.append("❌ Stochastic overbought")
            technical_details.append(f"Stochastic K at {stoch_k:.2f} (> 80)")
        
        # 3. VOLATILITY ANALYSIS
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
        if bb_position < 0.2:
            score += 1
            reasons.append("✅ Price at lower Bollinger Band (oversold)")
            technical_details.append(f"Price near BB Lower ({bb_lower:.2f})")
        elif bb_position > 0.8:
            score -= 1
            reasons.append("❌ Price at upper Bollinger Band (overbought)")
            technical_details.append(f"Price near BB Upper ({bb_upper:.2f})")
        
        # 4. TREND STRENGTH
        if adx > 25:
            if trend == 1:
                score += 1
                reasons.append("✅ Strong uptrend (ADX > 25)")
                technical_details.append(f"ADX at {adx:.2f} (strong trend)")
            elif trend == -1:
                score -= 1
                reasons.append("❌ Strong downtrend (ADX > 25)")
                technical_details.append(f"ADX at {adx:.2f} (strong downtrend)")
        
        # 5. SUPPORT/RESISTANCE ANALYSIS
        if support_levels:
            nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
            distance_to_support = ((current_price - nearest_support) / current_price) * 100
            
            if distance_to_support < 2:
                score += 2
                reasons.append(f"✅✅ Near strong support at ${nearest_support:,.2f}")
                technical_details.append(f"Support distance: {distance_to_support:.2f}%")
            elif distance_to_support < 5:
                score += 1
                reasons.append(f"✅ Approaching support at ${nearest_support:,.2f}")
                technical_details.append(f"Support distance: {distance_to_support:.2f}%")
        
        if resistance_levels:
            nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
            distance_to_resistance = ((nearest_resistance - current_price) / current_price) * 100
            
            if distance_to_resistance < 2:
                score -= 2
                reasons.append(f"❌❌ Near strong resistance at ${nearest_resistance:,.2f}")
                technical_details.append(f"Resistance distance: {distance_to_resistance:.2f}%")
        
        # 6. VOLUME ANALYSIS
        if current_volume > volume_sma * 1.5:
            if price_change_pct > 0:
                score += 1
                reasons.append("✅ High volume on price increase")
                technical_details.append(f"Volume: {current_volume/volume_sma:.2f}x average")
            else:
                score -= 1
                reasons.append("❌ High volume on price decrease")
                technical_details.append(f"Volume: {current_volume/volume_sma:.2f}x average")
        
        # 7. FEAR & GREED
        if fg_data:
            if fg_data.is_extreme_fear():
                score += 3
                reasons.append(f"✅✅✅ EXTREME FEAR ({fg_data.value}) - Contrarian buy!")
                technical_details.append("Market sentiment: Others panicking, opportunity to buy")
            elif fg_data.is_fear():
                score += 2
                reasons.append(f"✅✅ Fear ({fg_data.value}) - Good entry")
                technical_details.append("Market sentiment: Cautious, good for accumulation")
            elif fg_data.is_extreme_greed():
                score -= 3
                reasons.append(f"❌❌❌ EXTREME GREED ({fg_data.value}) - Take profits!")
                technical_details.append("Market sentiment: Euphoria, time to exit")
            elif fg_data.is_greed():
                score -= 2
                reasons.append(f"❌❌ Greed ({fg_data.value}) - Consider selling")
                technical_details.append("Market sentiment: Optimistic, watch for reversal")
        
        # 8. FIBONACCI ANALYSIS
        if fib_levels:
            fib_618 = fib_levels.get('level_618', 0)
            fib_382 = fib_levels.get('level_382', 0)
            
            if abs(current_price - fib_618) / current_price < 0.01:
                score += 1
                reasons.append(f"✅ Near Fibonacci 61.8% ({fib_618:.2f})")
                technical_details.append("Fibonacci: Key retracement level")
        
        # ========================================
        # DETERMINE RECOMMENDATION
        # ========================================
        
        if score >= 8:
            recommendation = "🟢 STRONG BUY"
            action = "BUY"
            confidence = "VERY HIGH"
        elif score >= 5:
            recommendation = "🟢 BUY"
            action = "BUY"
            confidence = "HIGH"
        elif score >= 2:
            recommendation = "🟡 WEAK BUY"
            action = "BUY"
            confidence = "MEDIUM"
        elif score <= -8:
            recommendation = "🔴 STRONG SELL"
            action = "SELL"
            confidence = "VERY HIGH"
        elif score <= -5:
            recommendation = "🔴 SELL"
            action = "SELL"
            confidence = "HIGH"
        elif score <= -2:
            recommendation = "🟠 WEAK SELL"
            action = "SELL"
            confidence = "MEDIUM"
        else:
            recommendation = "⚪ HOLD"
            action = "HOLD"
            confidence = "LOW"
        
        # ========================================
        # CALCULATE ENTRY/EXIT LEVELS
        # ========================================
        
        if action == "BUY":
            entry = current_price
            stop_loss = current_price - (2 * atr)
            take_profit_1 = current_price + (2 * atr)
            take_profit_2 = current_price + (3 * atr)
            take_profit_3 = current_price + (5 * atr)
            
            # Adjust based on support/resistance
            if support_levels:
                stop_loss = max(stop_loss, nearest_support * 0.99)
            if resistance_levels:
                take_profit_1 = min(take_profit_1, nearest_resistance)
            
            risk_pct = ((entry - stop_loss) / entry) * 100
            reward_pct = ((take_profit_2 - entry) / entry) * 100
            risk_reward = reward_pct / risk_pct if risk_pct > 0 else 0
            
        elif action == "SELL":
            entry = current_price
            stop_loss = current_price + (2 * atr)
            take_profit_1 = current_price - (2 * atr)
            take_profit_2 = current_price - (3 * atr)
            take_profit_3 = current_price - (5 * atr)
            
            risk_pct = ((stop_loss - entry) / entry) * 100
            reward_pct = ((entry - take_profit_2) / entry) * 100
            risk_reward = reward_pct / risk_pct if risk_pct > 0 else 0
            
        else:  # HOLD
            entry = current_price
            stop_loss = None
            take_profit_1 = None
            take_profit_2 = None
            take_profit_3 = None
            risk_pct = 0
            reward_pct = 0
            risk_reward = 0
        
        # ========================================
        # BUILD POSITION OBJECT
        # ========================================
        
        position = {
            'timeframe': timeframe,
            'timeframe_name': timeframe_name,
            'timestamp': datetime.now(),
            'current_price': current_price,
            'recommendation': recommendation,
            'action': action,
            'confidence': confidence,
            'score': score,
            'max_score': 20,  # Approximate maximum possible score
            
            # Entry/Exit levels
            'entry': entry,
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'take_profit_3': take_profit_3,
            'risk_pct': risk_pct,
            'reward_pct': reward_pct,
            'risk_reward_ratio': risk_reward,
            
            # Technical details
            'ema_12': ema_12,
            'ema_26': ema_26,
            'sma_50': sma_50,
            'sma_200': sma_200,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'stoch_k': stoch_k,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'atr': atr,
            'trend': trend,
            'adx': adx,
            'obv': obv,
            'volume_ratio': current_volume / volume_sma if volume_sma > 0 else 1,
            
            # Levels
            'support_levels': support_levels[:3] if support_levels else [],
            'resistance_levels': resistance_levels[:3] if resistance_levels else [],
            'fibonacci_levels': fib_levels,
            
            # Explanations
            'reasons': reasons,
            'technical_details': technical_details,
            
            # Fear & Greed
            'fear_greed_value': fg_data.value if fg_data else None,
            'fear_greed_classification': fg_data.classification if fg_data else None,
            
            # Data for plotting
            'dataframe': df,
            'analysis': analysis
        }
        
        return position
    
    def print_position_report(self, positions: List[Dict]):
        """Print comprehensive position report"""
        
        print("\n" + "="*100)
        print(f"{'MULTI-TIMEFRAME POSITION ANALYSIS REPORT':^100}")
        print("="*100)
        print(f"\n📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💰 Current BTC Price: ${positions[0]['current_price']:,.2f}" if positions else "")
        
        if positions and positions[0]['fear_greed_value']:
            print(f"😱 Fear & Greed Index: {positions[0]['fear_greed_value']} ({positions[0]['fear_greed_classification']})")
        
        print("\n" + "="*100)
        
        for i, pos in enumerate(positions, 1):
            print(f"\n{'─'*100}")
            print(f"POSITION #{i}: {pos['timeframe_name'].upper()} TIMEFRAME ({pos['timeframe']})")
            print(f"{'─'*100}")
            
            # Header
            print(f"\n💡 RECOMMENDATION: {pos['recommendation']}")
            print(f"   Action: {pos['action']}")
            print(f"   Confidence: {pos['confidence']}")
            print(f"   Score: {pos['score']}/{pos['max_score']}")
            
            # Entry/Exit if not HOLD
            if pos['action'] != "HOLD":
                print(f"\n🎯 TRADE SETUP:")
                print(f"   Entry Price:     ${pos['entry']:,.2f}")
                print(f"   Stop Loss:       ${pos['stop_loss']:,.2f} ({pos['risk_pct']:.2f}% risk)")
                print(f"   Take Profit 1:   ${pos['take_profit_1']:,.2f}")
                print(f"   Take Profit 2:   ${pos['take_profit_2']:,.2f} ({pos['reward_pct']:.2f}% gain)")
                print(f"   Take Profit 3:   ${pos['take_profit_3']:,.2f}")
                print(f"   Risk:Reward:     1:{pos['risk_reward_ratio']:.2f}")
            
            # Technical Indicators
            print(f"\n📊 TECHNICAL INDICATORS:")
            print(f"   EMA 12:          ${pos['ema_12']:,.2f}")
            print(f"   EMA 26:          ${pos['ema_26']:,.2f}")
            print(f"   SMA 50:          ${pos['sma_50']:,.2f}")
            print(f"   SMA 200:         ${pos['sma_200']:,.2f}")
            print(f"   RSI:             {pos['rsi']:.2f}")
            print(f"   MACD:            {pos['macd']:.2f}")
            print(f"   MACD Signal:     {pos['macd_signal']:.2f}")
            print(f"   Stochastic K:    {pos['stoch_k']:.2f}")
            print(f"   ADX (Strength):  {pos['adx']:.2f}")
            print(f"   ATR:             ${pos['atr']:,.2f}")
            print(f"   Volume Ratio:    {pos['volume_ratio']:.2f}x")
            
            # Bollinger Bands
            print(f"\n📈 BOLLINGER BANDS:")
            print(f"   Upper:           ${pos['bb_upper']:,.2f}")
            print(f"   Middle:          ${pos['bb_middle']:,.2f}")
            print(f"   Lower:           ${pos['bb_lower']:,.2f}")
            
            # Support/Resistance
            if pos['support_levels']:
                print(f"\n🎯 KEY SUPPORT LEVELS:")
                for j, level in enumerate(pos['support_levels'], 1):
                    print(f"   Support {j}:       ${level:,.2f}")
            
            if pos['resistance_levels']:
                print(f"\n🎯 KEY RESISTANCE LEVELS:")
                for j, level in enumerate(pos['resistance_levels'], 1):
                    print(f"   Resistance {j}:    ${level:,.2f}")
            
            # Fibonacci
            if pos['fibonacci_levels']:
                print(f"\n📐 FIBONACCI RETRACEMENT:")
                for level_name, level_value in list(pos['fibonacci_levels'].items())[:4]:
                    print(f"   {level_name}:    ${level_value:,.2f}")
            
            # Reasons
            print(f"\n💭 ANALYSIS & REASONING:")
            for reason in pos['reasons'][:10]:  # Show top 10 reasons
                print(f"   {reason}")
            
            # Technical Details
            print(f"\n🔍 DETAILED TECHNICAL ANALYSIS:")
            for detail in pos['technical_details'][:8]:  # Show top 8 details
                print(f"   {detail}")
        
        print("\n" + "="*100)
        print(f"{'END OF REPORT':^100}")
        print("="*100 + "\n")
    
    def plot_positions_with_markers(self, positions: List[Dict], save_path: str = "multi_timeframe_positions.png"):
        """Plot charts for all timeframes with position markers"""
        
        num_positions = len(positions)
        fig, axes = plt.subplots(num_positions, 1, figsize=(16, 6 * num_positions))
        
        if num_positions == 1:
            axes = [axes]
        
        fig.suptitle('Multi-Timeframe Position Analysis with Entry/Exit Markers', 
                    fontsize=16, fontweight='bold')
        
        for idx, (ax, pos) in enumerate(zip(axes, positions)):
            df = pos['dataframe']
            analysis = pos['analysis']
            
            # Plot price
            ax.plot(df.index, df['close'], label='Price', color='black', linewidth=2, zorder=5)
            
            # Plot EMAs
            ax.plot(df.index, analysis['ema_12'], label='EMA 12', color='blue', alpha=0.7, linewidth=1.5)
            ax.plot(df.index, analysis['ema_26'], label='EMA 26', color='red', alpha=0.7, linewidth=1.5)
            ax.plot(df.index, analysis['sma_50'], label='SMA 50', color='orange', alpha=0.6, linewidth=1)
            ax.plot(df.index, analysis['sma_200'], label='SMA 200', color='purple', alpha=0.5, linewidth=1.5)
            
            # Plot Bollinger Bands
            ax.plot(df.index, analysis['bb_upper'], 'g--', alpha=0.3, linewidth=1)
            ax.plot(df.index, analysis['bb_lower'], 'r--', alpha=0.3, linewidth=1)
            ax.fill_between(df.index, analysis['bb_upper'], analysis['bb_lower'], alpha=0.1, color='gray')
            
            # Plot support/resistance
            for level in pos['support_levels'][:2]:
                ax.axhline(y=level, color='green', linestyle=':', alpha=0.5, linewidth=1.5, label=f'Support ${level:,.0f}')
            
            for level in pos['resistance_levels'][:2]:
                ax.axhline(y=level, color='red', linestyle=':', alpha=0.5, linewidth=1.5, label=f'Resistance ${level:,.0f}')
            
            # Mark current position with X
            current_time = df.index[-1]
            current_price = pos['current_price']
            
            # Entry marker
            if pos['action'] != "HOLD":
                marker_color = 'green' if pos['action'] == 'BUY' else 'red'
                marker_style = '^' if pos['action'] == 'BUY' else 'v'
                marker_size = 300
                
                ax.scatter([current_time], [pos['entry']], 
                          color=marker_color, marker=marker_style, s=marker_size, 
                          edgecolors='black', linewidths=2, zorder=10,
                          label=f"{pos['action']} @ ${pos['entry']:,.0f}")
                
                # Stop loss and take profit lines
                if pos['stop_loss']:
                    ax.axhline(y=pos['stop_loss'], color='red', linestyle='--', 
                              alpha=0.7, linewidth=2, label=f"Stop Loss ${pos['stop_loss']:,.0f}")
                
                if pos['take_profit_2']:
                    ax.axhline(y=pos['take_profit_2'], color='green', linestyle='--', 
                              alpha=0.7, linewidth=2, label=f"Take Profit ${pos['take_profit_2']:,.0f}")
            
            # Formatting
            ax.set_title(f"{pos['timeframe_name']} - {pos['recommendation']} (Score: {pos['score']}/{pos['max_score']})",
                        fontsize=14, fontweight='bold')
            ax.set_ylabel('Price (USD)', fontsize=11)
            ax.legend(loc='upper left', fontsize=8, ncol=2)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            # Add text box with key info
            info_text = f"RSI: {pos['rsi']:.1f} | MACD: {pos['macd']:.1f} | ADX: {pos['adx']:.1f}"
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                   fontsize=9)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        logger.info(f"✅ Charts saved to {save_path}")
        plt.close()
        
        return save_path


# Example usage
if __name__ == "__main__":
    print("="*100)
    print(f"{'MULTI-TIMEFRAME POSITION ANALYZER':^100}")
    print("="*100)
    
    analyzer = MultiTimeframePositionAnalyzer()
    
    # Analyze all timeframes
    positions = analyzer.analyze_all_timeframes("BTCUSDT")
    
    # Print report
    analyzer.print_position_report(positions)
    
    # Plot charts
    analyzer.plot_positions_with_markers(positions)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Charts saved to: multi_timeframe_positions.png")
    print(f"📋 {len(positions)} position suggestions generated")

