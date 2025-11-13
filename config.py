"""
Configuration Module
====================
Centralized configuration for the Bitcoin Trading System
"""

from dataclasses import dataclass
from typing import Optional
import os
import json


@dataclass
class TradingConfig:
    """Trading strategy configuration"""
    # EMA Settings
    ema_fast: int = 20
    ema_slow: int = 50
    
    # RSI Settings
    rsi_period: int = 14
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    rsi_exit: int = 80
    
    # MACD Settings
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # Fibonacci Settings
    fib_lookback: int = 100
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'ema_fast': self.ema_fast,
            'ema_slow': self.ema_slow,
            'rsi_period': self.rsi_period,
            'rsi_overbought': self.rsi_overbought,
            'rsi_oversold': self.rsi_oversold,
            'rsi_exit': self.rsi_exit,
            'macd_fast': self.macd_fast,
            'macd_slow': self.macd_slow,
            'macd_signal': self.macd_signal,
            'fib_lookback': self.fib_lookback
        }


@dataclass
class RiskConfig:
    """Risk management configuration"""
    initial_capital: float = 10000.0
    max_position_size_pct: float = 100.0
    max_risk_per_trade_pct: float = 2.0
    max_daily_loss_pct: float = 5.0
    max_open_positions: int = 1
    min_risk_reward_ratio: float = 1.5
    use_trailing_stop: bool = True
    trailing_stop_pct: float = 2.0


@dataclass
class DataConfig:
    """Data streaming configuration"""
    symbol: str = "btcusdt"
    interval: str = "1m"
    max_buffer_size: int = 1000
    reconnect_delay: int = 5
    max_reconnect_attempts: int = 10


@dataclass
class WebhookConfig:
    """Webhook configuration"""
    enabled: bool = False
    discord_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    custom_webhook_url: Optional[str] = None


@dataclass
class SystemConfig:
    """Complete system configuration"""
    trading: TradingConfig
    risk: RiskConfig
    data: DataConfig
    webhook: WebhookConfig
    
    # System settings
    enable_paper_trading: bool = True
    enable_risk_management: bool = True
    enable_fear_greed_index: bool = True
    log_level: str = "INFO"
    log_file: str = "trading_system.log"
    
    @classmethod
    def load_from_file(cls, filepath: str = "config.json"):
        """Load configuration from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                return cls(
                    trading=TradingConfig(**data.get('trading', {})),
                    risk=RiskConfig(**data.get('risk', {})),
                    data=DataConfig(**data.get('data', {})),
                    webhook=WebhookConfig(**data.get('webhook', {})),
                    **{k: v for k, v in data.items() if k not in ['trading', 'risk', 'data', 'webhook']}
                )
        return cls(
            trading=TradingConfig(),
            risk=RiskConfig(),
            data=DataConfig(),
            webhook=WebhookConfig()
        )
    
    def save_to_file(self, filepath: str = "config.json"):
        """Save configuration to JSON file"""
        data = {
            'trading': self.trading.__dict__,
            'risk': self.risk.__dict__,
            'data': self.data.__dict__,
            'webhook': self.webhook.__dict__,
            'enable_paper_trading': self.enable_paper_trading,
            'enable_risk_management': self.enable_risk_management,
            'enable_fear_greed_index': self.enable_fear_greed_index,
            'log_level': self.log_level,
            'log_file': self.log_file
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Default configuration
DEFAULT_CONFIG = SystemConfig(
    trading=TradingConfig(),
    risk=RiskConfig(),
    data=DataConfig(),
    webhook=WebhookConfig()
)

