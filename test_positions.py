"""
Position Testing Script
=======================
Comprehensive testing of trading positions with simulated scenarios
"""

import asyncio
import logging
from datetime import datetime, timedelta
import random
from typing import List
import pandas as pd

from config import SystemConfig, TradingConfig, RiskConfig, DataConfig
from position_tracker import PositionTracker
from fear_greed_index import FearGreedIndexFetcher, FearGreedData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PositionTester:
    """Test trading positions with various scenarios"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.tracker = PositionTracker(initial_capital=initial_capital)
        self.fear_greed_fetcher = FearGreedIndexFetcher()
    
    def test_winning_trade(self):
        """Test a winning trade scenario"""
        logger.info("\n" + "="*70)
        logger.info("TEST 1: WINNING TRADE")
        logger.info("="*70)
        
        # Open position
        pos = self.tracker.open_position(
            entry_price=50000.0,
            position_size=0.1,
            stop_loss_price=49000.0,
            take_profit_price=52000.0,
            trailing_stop_pct=2.0,
            entry_reason="Test winning trade",
            signal_confidence=0.85
        )
        
        if pos:
            # Simulate price going up
            self.tracker.update_open_positions(50500.0)
            self.tracker.update_open_positions(51000.0)
            self.tracker.update_open_positions(51500.0)
            
            # Close at profit
            self.tracker.close_position(pos, 52000.0, "Take profit reached")
    
    def test_losing_trade(self):
        """Test a losing trade scenario"""
        logger.info("\n" + "="*70)
        logger.info("TEST 2: LOSING TRADE")
        logger.info("="*70)
        
        pos = self.tracker.open_position(
            entry_price=50000.0,
            position_size=0.1,
            stop_loss_price=49000.0,
            take_profit_price=52000.0,
            entry_reason="Test losing trade"
        )
        
        if pos:
            # Simulate price going down
            self.tracker.update_open_positions(49800.0)
            self.tracker.update_open_positions(49500.0)
            self.tracker.update_open_positions(49200.0)
            
            # Stop loss triggered
            self.tracker.close_position(pos, 49000.0, "Stop loss triggered")
    
    def test_trailing_stop(self):
        """Test trailing stop functionality"""
        logger.info("\n" + "="*70)
        logger.info("TEST 3: TRAILING STOP")
        logger.info("="*70)
        
        pos = self.tracker.open_position(
            entry_price=50000.0,
            position_size=0.1,
            stop_loss_price=49000.0,
            take_profit_price=53000.0,
            trailing_stop_pct=2.0,
            entry_reason="Test trailing stop"
        )
        
        if pos:
            # Price goes up (trailing stop moves up)
            self.tracker.update_open_positions(50500.0)
            self.tracker.update_open_positions(51000.0)
            self.tracker.update_open_positions(51500.0)
            self.tracker.update_open_positions(52000.0)
            
            # Price drops back (hits trailing stop)
            self.tracker.update_open_positions(51500.0)
            self.tracker.update_open_positions(51000.0)
            
            # Check if stopped out
            if pos.should_stop_out():
                self.tracker.close_position(pos, pos.current_price, "Trailing stop triggered")
    
    def test_multiple_positions(self):
        """Test multiple positions"""
        logger.info("\n" + "="*70)
        logger.info("TEST 4: MULTIPLE TRADES SEQUENCE")
        logger.info("="*70)
        
        scenarios = [
            (50000, 52000, True),   # Win
            (52000, 51000, False),  # Loss
            (51000, 53000, True),   # Win
            (53000, 54500, True),   # Win
            (54500, 53500, False),  # Loss
        ]
        
        for i, (entry, exit, is_win) in enumerate(scenarios, 1):
            logger.info(f"\n--- Trade {i} ---")
            
            pos = self.tracker.open_position(
                entry_price=entry,
                position_size=0.05,
                stop_loss_price=entry * 0.98,
                take_profit_price=entry * 1.04,
                entry_reason=f"Scenario {i} - {'Win' if is_win else 'Loss'}"
            )
            
            if pos:
                # Simulate some price movement
                mid_price = (entry + exit) / 2
                self.tracker.update_open_positions(mid_price)
                self.tracker.update_open_positions(exit)
                
                # Close position
                reason = "Take profit" if is_win else "Stop loss"
                self.tracker.close_position(pos, exit, reason)
    
    def test_with_fear_greed(self):
        """Test positions with Fear & Greed Index integration"""
        logger.info("\n" + "="*70)
        logger.info("TEST 5: FEAR & GREED INDEX INTEGRATION")
        logger.info("="*70)
        
        # Fetch current Fear & Greed
        fg_data = self.fear_greed_fetcher.fetch_current()
        
        if fg_data:
            logger.info(f"Current Fear & Greed: {fg_data.value} ({fg_data.classification})")
            
            # Test scenarios based on sentiment
            scenarios = [
                (45000, "Extreme Fear scenario", 25),
                (48000, "Fear scenario", 40),
                (50000, "Neutral scenario", 50),
                (52000, "Greed scenario", 65),
                (55000, "Extreme Greed scenario", 80),
            ]
            
            for entry_price, description, fg_value in scenarios:
                logger.info(f"\n--- {description} ---")
                
                # Simulate Fear & Greed data
                simulated_fg = FearGreedData(
                    value=fg_value,
                    classification=self._get_fg_classification(fg_value),
                    timestamp=datetime.now()
                )
                
                pos = self.tracker.open_position(
                    entry_price=entry_price,
                    position_size=0.02,
                    stop_loss_price=entry_price * 0.98,
                    take_profit_price=entry_price * 1.05,
                    entry_reason=description,
                    fear_greed_value=simulated_fg.value
                )
                
                if pos:
                    # Simulate outcome based on sentiment
                    if fg_value < 30:  # Extreme fear - likely to go up
                        exit_price = entry_price * 1.05
                    elif fg_value > 70:  # Extreme greed - likely to go down
                        exit_price = entry_price * 0.98
                    else:  # Neutral
                        exit_price = entry_price * (1 + random.uniform(-0.02, 0.03))
                    
                    self.tracker.update_open_positions(exit_price)
                    self.tracker.close_position(pos, exit_price, "Scenario complete")
    
    def _get_fg_classification(self, value: int) -> str:
        """Get Fear & Greed classification from value"""
        if value < 25:
            return "Extreme Fear"
        elif value < 45:
            return "Fear"
        elif value < 55:
            return "Neutral"
        elif value < 75:
            return "Greed"
        else:
            return "Extreme Greed"
    
    def test_risk_scenarios(self):
        """Test various risk scenarios"""
        logger.info("\n" + "="*70)
        logger.info("TEST 6: RISK MANAGEMENT SCENARIOS")
        logger.info("="*70)
        
        # Scenario 1: Large position size
        logger.info("\n--- Large Position Size ---")
        pos1 = self.tracker.open_position(
            entry_price=50000.0,
            position_size=0.15,
            stop_loss_price=49000.0,
            take_profit_price=51000.0,
            entry_reason="Large position test"
        )
        if pos1:
            self.tracker.update_open_positions(49500.0)
            self.tracker.close_position(pos1, 49000.0, "Stop loss - large position")
        
        # Scenario 2: Tight stop loss
        logger.info("\n--- Tight Stop Loss ---")
        pos2 = self.tracker.open_position(
            entry_price=50000.0,
            position_size=0.1,
            stop_loss_price=49900.0,  # Only 0.2% stop
            take_profit_price=51000.0,
            entry_reason="Tight stop loss test"
        )
        if pos2:
            self.tracker.update_open_positions(49950.0)
            self.tracker.update_open_positions(49900.0)
            if pos2.should_stop_out():
                self.tracker.close_position(pos2, 49900.0, "Tight stop loss triggered")
        
        # Scenario 3: Wide stop loss, large target
        logger.info("\n--- Wide Stop, Large Target ---")
        pos3 = self.tracker.open_position(
            entry_price=50000.0,
            position_size=0.05,
            stop_loss_price=48000.0,  # 4% stop
            take_profit_price=54000.0,  # 8% target
            entry_reason="Wide stop, large target test"
        )
        if pos3:
            # Simulate volatile movement
            prices = [50500, 51000, 50500, 51500, 52000, 53000, 54000]
            for p in prices:
                self.tracker.update_open_positions(p)
            self.tracker.close_position(pos3, 54000.0, "Large target reached")
    
    def run_all_tests(self):
        """Run all position tests"""
        logger.info("\n" + "🔬" + "="*68 + "🔬")
        logger.info("  COMPREHENSIVE POSITION TESTING SUITE")
        logger.info("🔬" + "="*68 + "🔬")
        
        # Run each test
        self.test_winning_trade()
        self.test_losing_trade()
        self.test_trailing_stop()
        self.test_multiple_positions()
        self.test_with_fear_greed()
        self.test_risk_scenarios()
        
        # Print final summary
        logger.info("\n" + "="*70)
        logger.info("🎯 TESTING COMPLETE - FINAL RESULTS")
        logger.info("="*70)
        self.tracker.print_summary()
        
        # Save results
        self.tracker.save_to_file("test_positions_results.json")
        logger.info("Test results saved to test_positions_results.json")


async def test_live_simulation():
    """Test with live market data (simulated)"""
    logger.info("\n" + "="*70)
    logger.info("LIVE SIMULATION TEST")
    logger.info("="*70)
    logger.info("Simulating 24 hours of trading with realistic price action...")
    
    tracker = PositionTracker(initial_capital=10000.0)
    
    # Simulate 24 hours, checking every minute
    base_price = 50000.0
    current_price = base_price
    
    for minute in range(1440):  # 24 * 60 minutes
        # Simulate price movement (random walk with drift)
        change_pct = random.gauss(0.0001, 0.002)  # Small random changes
        current_price *= (1 + change_pct)
        
        # Randomly generate signals (simplified)
        if minute % 120 == 0 and len(tracker.open_positions) == 0:
            # Open position every 2 hours if no position open
            pos = tracker.open_position(
                entry_price=current_price,
                position_size=0.05,
                stop_loss_price=current_price * 0.98,
                take_profit_price=current_price * 1.03,
                trailing_stop_pct=1.5,
                entry_reason=f"Simulated signal at minute {minute}"
            )
        
        # Update open positions
        tracker.update_open_positions(current_price)
        
        # Log progress every hour
        if minute % 60 == 0:
            hour = minute // 60
            logger.info(f"Hour {hour:2d}: Price ${current_price:,.2f} | "
                       f"Open positions: {len(tracker.open_positions)} | "
                       f"Capital: ${tracker.current_capital:,.2f}")
        
        # Small delay to simulate time passing
        await asyncio.sleep(0.01)
    
    # Close any remaining positions
    tracker.close_all_positions(current_price, "Simulation ended")
    
    # Print summary
    tracker.print_summary()
    
    return tracker


def main():
    """Main entry point for testing"""
    print("\n" + "="*70)
    print("🧪 BITCOIN TRADING POSITION TESTER")
    print("="*70)
    print("\nSelect test mode:")
    print("1. Run all unit tests")
    print("2. Run live simulation (24 hours)")
    print("3. Run both")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1" or choice == "3":
        tester = PositionTester(initial_capital=10000.0)
        tester.run_all_tests()
    
    if choice == "2" or choice == "3":
        if choice == "3":
            input("\nPress Enter to continue to live simulation...")
        asyncio.run(test_live_simulation())
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    main()

