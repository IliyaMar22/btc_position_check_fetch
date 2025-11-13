"""
Position Tracker Module
========================
Track and manage paper trading positions with detailed metrics
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class PositionStatus(Enum):
    """Position status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    STOPPED_OUT = "stopped_out"
    TAKE_PROFIT = "take_profit"


@dataclass
class Position:
    """Trading position data structure"""
    # Entry information
    entry_time: datetime
    entry_price: float
    position_size: float  # In BTC
    position_value: float  # In USD
    
    # Exit information
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    
    # Risk management
    stop_loss_price: float = 0.0
    take_profit_price: float = 0.0
    trailing_stop_pct: float = 0.0
    current_stop_loss: float = 0.0
    
    # Position tracking
    highest_price: float = 0.0
    lowest_price: float = 0.0
    current_price: float = 0.0
    
    # Performance metrics
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    realized_pnl: float = 0.0
    realized_pnl_pct: float = 0.0
    
    # Status
    status: PositionStatus = PositionStatus.OPEN
    
    # Metadata
    entry_reason: str = ""
    exit_reason: str = ""
    signal_confidence: float = 1.0
    fear_greed_value: Optional[int] = None
    
    # Trade ID
    trade_id: str = field(default_factory=lambda: f"TRADE_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    def update_price(self, current_price: float):
        """Update position with current market price"""
        self.current_price = current_price
        
        # Update highest/lowest
        if current_price > self.highest_price:
            self.highest_price = current_price
        if self.lowest_price == 0 or current_price < self.lowest_price:
            self.lowest_price = current_price
        
        # Calculate unrealized P&L
        self.unrealized_pnl = (current_price - self.entry_price) * self.position_size
        self.unrealized_pnl_pct = ((current_price - self.entry_price) / self.entry_price) * 100
        
        # Update trailing stop if enabled
        if self.trailing_stop_pct > 0:
            new_stop = self.highest_price * (1 - self.trailing_stop_pct / 100)
            if new_stop > self.current_stop_loss:
                self.current_stop_loss = new_stop
                logger.info(f"🔄 Trailing stop updated: ${self.current_stop_loss:,.2f}")
    
    def should_stop_out(self) -> bool:
        """Check if position should be stopped out"""
        if self.current_stop_loss > 0 and self.current_price <= self.current_stop_loss:
            return True
        if self.stop_loss_price > 0 and self.current_price <= self.stop_loss_price:
            return True
        return False
    
    def should_take_profit(self) -> bool:
        """Check if take profit level is hit"""
        if self.take_profit_price > 0 and self.current_price >= self.take_profit_price:
            return True
        return False
    
    def close(self, exit_price: float, exit_reason: str):
        """Close the position"""
        self.exit_time = datetime.now()
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        
        # Calculate realized P&L
        self.realized_pnl = (exit_price - self.entry_price) * self.position_size
        self.realized_pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        
        # Update status
        if "stop" in exit_reason.lower():
            self.status = PositionStatus.STOPPED_OUT
        elif "profit" in exit_reason.lower():
            self.status = PositionStatus.TAKE_PROFIT
        else:
            self.status = PositionStatus.CLOSED
        
        logger.info(f"📍 Position closed: {self.exit_reason}")
        logger.info(f"   PnL: ${self.realized_pnl:.2f} ({self.realized_pnl_pct:.2f}%)")
    
    def get_duration(self) -> str:
        """Get position duration as string"""
        if self.exit_time:
            duration = self.exit_time - self.entry_time
        else:
            duration = datetime.now() - self.entry_time
        
        hours = duration.total_seconds() / 3600
        if hours < 1:
            return f"{duration.total_seconds() / 60:.0f}m"
        elif hours < 24:
            return f"{hours:.1f}h"
        else:
            days = hours / 24
            return f"{days:.1f}d"
    
    def to_dict(self) -> Dict:
        """Convert position to dictionary"""
        return {
            'trade_id': self.trade_id,
            'entry_time': self.entry_time.isoformat(),
            'entry_price': self.entry_price,
            'position_size': self.position_size,
            'position_value': self.position_value,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'exit_price': self.exit_price,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price,
            'realized_pnl': self.realized_pnl,
            'realized_pnl_pct': self.realized_pnl_pct,
            'status': self.status.value,
            'entry_reason': self.entry_reason,
            'exit_reason': self.exit_reason,
            'duration': self.get_duration(),
            'fear_greed_value': self.fear_greed_value
        }
    
    def __str__(self) -> str:
        """String representation"""
        if self.status == PositionStatus.OPEN:
            return (f"Position {self.trade_id}: OPEN\n"
                   f"  Entry: ${self.entry_price:,.2f} @ {self.entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                   f"  Current: ${self.current_price:,.2f}\n"
                   f"  Unrealized P&L: ${self.unrealized_pnl:.2f} ({self.unrealized_pnl_pct:+.2f}%)\n"
                   f"  Duration: {self.get_duration()}")
        else:
            return (f"Position {self.trade_id}: {self.status.value.upper()}\n"
                   f"  Entry: ${self.entry_price:,.2f} @ {self.entry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                   f"  Exit: ${self.exit_price:,.2f} @ {self.exit_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                   f"  Realized P&L: ${self.realized_pnl:.2f} ({self.realized_pnl_pct:+.2f}%)\n"
                   f"  Duration: {self.get_duration()}")


class PositionTracker:
    """Track all trading positions and calculate portfolio metrics"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.open_positions: List[Position] = []
        self.closed_positions: List[Position] = []
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        
        # Daily tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.current_date = datetime.now().date()
    
    def open_position(self, 
                     entry_price: float,
                     position_size: float,
                     stop_loss_price: float = 0.0,
                     take_profit_price: float = 0.0,
                     trailing_stop_pct: float = 0.0,
                     entry_reason: str = "",
                     signal_confidence: float = 1.0,
                     fear_greed_value: Optional[int] = None) -> Optional[Position]:
        """
        Open a new position
        
        Returns:
            Position object or None if unable to open
        """
        position_value = entry_price * position_size
        
        # Check if we have enough capital
        if position_value > self.current_capital:
            logger.warning(f"Insufficient capital: ${self.current_capital:.2f} < ${position_value:.2f}")
            return None
        
        position = Position(
            entry_time=datetime.now(),
            entry_price=entry_price,
            position_size=position_size,
            position_value=position_value,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            trailing_stop_pct=trailing_stop_pct,
            current_stop_loss=stop_loss_price,
            highest_price=entry_price,
            lowest_price=entry_price,
            current_price=entry_price,
            entry_reason=entry_reason,
            signal_confidence=signal_confidence,
            fear_greed_value=fear_greed_value
        )
        
        self.open_positions.append(position)
        self.total_trades += 1
        self.daily_trades += 1
        
        logger.info("="*70)
        logger.info(f"🟢 OPENED POSITION: {position.trade_id}")
        logger.info(f"   Entry Price: ${entry_price:,.2f}")
        logger.info(f"   Position Size: {position_size:.6f} BTC (${position_value:,.2f})")
        logger.info(f"   Stop Loss: ${stop_loss_price:,.2f}" if stop_loss_price > 0 else "   Stop Loss: None")
        logger.info(f"   Take Profit: ${take_profit_price:,.2f}" if take_profit_price > 0 else "   Take Profit: None")
        logger.info(f"   Reason: {entry_reason}")
        if fear_greed_value is not None:
            logger.info(f"   Fear & Greed: {fear_greed_value}/100")
        logger.info("="*70)
        
        return position
    
    def update_open_positions(self, current_price: float):
        """Update all open positions with current price"""
        for position in self.open_positions:
            position.update_price(current_price)
            
            # Check for automatic exits
            if position.should_stop_out():
                self.close_position(position, current_price, "Stop loss triggered")
            elif position.should_take_profit():
                self.close_position(position, current_price, "Take profit target reached")
    
    def close_position(self, position: Position, exit_price: float, exit_reason: str):
        """Close a position"""
        if position not in self.open_positions:
            logger.warning(f"Position {position.trade_id} not found in open positions")
            return
        
        position.close(exit_price, exit_reason)
        
        # Update capital
        self.current_capital += position.realized_pnl
        self.total_pnl += position.realized_pnl
        self.daily_pnl += position.realized_pnl
        
        # Update statistics
        if position.realized_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Move to closed positions
        self.open_positions.remove(position)
        self.closed_positions.append(position)
        
        logger.info("="*70)
        logger.info(f"🔴 CLOSED POSITION: {position.trade_id}")
        logger.info(f"   Exit Price: ${exit_price:,.2f}")
        logger.info(f"   P&L: ${position.realized_pnl:,.2f} ({position.realized_pnl_pct:+.2f}%)")
        logger.info(f"   Duration: {position.get_duration()}")
        logger.info(f"   Reason: {exit_reason}")
        logger.info(f"   New Capital: ${self.current_capital:,.2f}")
        logger.info("="*70)
    
    def close_all_positions(self, current_price: float, exit_reason: str = "Close all"):
        """Close all open positions"""
        for position in self.open_positions.copy():
            self.close_position(position, current_price, exit_reason)
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary"""
        # Check for day change
        today = datetime.now().date()
        if today != self.current_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.current_date = today
        
        # Calculate metrics
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        winning_pnl = sum(p.realized_pnl for p in self.closed_positions if p.realized_pnl > 0)
        losing_pnl = abs(sum(p.realized_pnl for p in self.closed_positions if p.realized_pnl < 0))
        profit_factor = (winning_pnl / losing_pnl) if losing_pnl > 0 else float('inf')
        
        total_return_pct = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        
        avg_win = (winning_pnl / self.winning_trades) if self.winning_trades > 0 else 0
        avg_loss = (losing_pnl / self.losing_trades) if self.losing_trades > 0 else 0
        
        # Open positions P&L
        open_pnl = sum(p.unrealized_pnl for p in self.open_positions)
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'total_return': self.current_capital - self.initial_capital,
            'total_return_pct': total_return_pct,
            'total_trades': self.total_trades,
            'open_positions': len(self.open_positions),
            'closed_positions': len(self.closed_positions),
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': self.total_pnl,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'open_pnl': open_pnl
        }
    
    def print_summary(self):
        """Print formatted portfolio summary"""
        summary = self.get_portfolio_summary()
        
        print("\n" + "="*70)
        print("📊 PORTFOLIO SUMMARY")
        print("="*70)
        print(f"Initial Capital:      ${summary['initial_capital']:,.2f}")
        print(f"Current Capital:      ${summary['current_capital']:,.2f}")
        print(f"Total Return:         ${summary['total_return']:,.2f} ({summary['total_return_pct']:+.2f}%)")
        print(f"\n📈 TRADING STATISTICS")
        print(f"Total Trades:         {summary['total_trades']}")
        print(f"Open Positions:       {summary['open_positions']}")
        print(f"Closed Positions:     {summary['closed_positions']}")
        print(f"Winning Trades:       {summary['winning_trades']}")
        print(f"Losing Trades:        {summary['losing_trades']}")
        print(f"Win Rate:             {summary['win_rate']:.2f}%")
        print(f"Profit Factor:        {summary['profit_factor']:.2f}")
        print(f"\n💰 PERFORMANCE")
        print(f"Total P&L:            ${summary['total_pnl']:,.2f}")
        print(f"Today's P&L:          ${summary['daily_pnl']:,.2f}")
        print(f"Today's Trades:       {summary['daily_trades']}")
        print(f"Avg Win:              ${summary['avg_win']:,.2f}")
        print(f"Avg Loss:             ${summary['avg_loss']:,.2f}")
        
        if self.open_positions:
            print(f"\n🔓 OPEN POSITIONS")
            for pos in self.open_positions:
                print(f"\n{pos}")
        
        print("="*70 + "\n")
    
    def save_to_file(self, filepath: str = "positions_log.json"):
        """Save all positions to file"""
        data = {
            'summary': self.get_portfolio_summary(),
            'open_positions': [p.to_dict() for p in self.open_positions],
            'closed_positions': [p.to_dict() for p in self.closed_positions]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Positions saved to {filepath}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Position Tracker Demo")
    print("="*70)
    
    tracker = PositionTracker(initial_capital=10000.0)
    
    # Open a position
    pos1 = tracker.open_position(
        entry_price=50000.0,
        position_size=0.1,
        stop_loss_price=49000.0,
        take_profit_price=52000.0,
        trailing_stop_pct=2.0,
        entry_reason="EMA crossover + bullish RSI",
        signal_confidence=0.85,
        fear_greed_value=35
    )
    
    # Simulate price updates
    tracker.update_open_positions(50500.0)
    tracker.update_open_positions(51000.0)
    tracker.update_open_positions(51500.0)
    
    # Close position
    tracker.close_position(pos1, 51500.0, "Manual exit")
    
    # Print summary
    tracker.print_summary()
    
    # Save to file
    tracker.save_to_file()

