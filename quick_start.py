"""
Quick Start Script
==================
Easy launcher for the improved Bitcoin trading system
"""

import sys
import asyncio


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║          🚀 IMPROVED BITCOIN TRADING SYSTEM 🚀                   ║
    ║                                                                  ║
    ║          ✨ NEW FEATURES:                                        ║
    ║          • Fear & Greed Index Integration                        ║
    ║          • Advanced Position Tracking                            ║
    ║          • Enhanced WebSocket with Auto-Reconnect                ║
    ║          • Trailing Stop-Loss                                    ║
    ║          • Comprehensive Testing Suite                           ║
    ║          • JSON Configuration Management                         ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print("QUICK START MENU")
    print("="*70)
    print("\n📊 TESTING & ANALYSIS")
    print("  1. Test Positions (Recommended First!)")
    print("  2. Check Fear & Greed Index")
    print("  3. Test Enhanced WebSocket")
    print()
    print("🔴 LIVE TRADING (Paper)")
    print("  4. Run Improved Trading Engine")
    print("  5. Run Original Trading System")
    print()
    print("⚙️  CONFIGURATION")
    print("  6. Create/Edit Configuration")
    print("  7. View Current Configuration")
    print()
    print("📈 BACKTESTING & OPTIMIZATION")
    print("  8. Run Backtest")
    print("  9. Optimize Parameters")
    print()
    print("  0. Exit")
    print("="*70)


def test_positions():
    """Run position testing"""
    print("\n🧪 Running Position Tests...")
    import test_positions
    test_positions.main()


def check_fear_greed():
    """Check Fear & Greed Index"""
    print("\n😱 Fetching Fear & Greed Index...")
    import subprocess
    subprocess.run([sys.executable, "fear_greed_index.py"])


def test_websocket():
    """Test enhanced WebSocket"""
    print("\n📡 Testing Enhanced WebSocket...")
    print("Press Ctrl+C to stop")
    import subprocess
    subprocess.run([sys.executable, "enhanced_websocket.py"])


def run_improved_engine():
    """Run improved trading engine"""
    print("\n🚀 Starting Improved Trading Engine...")
    print("Press Ctrl+C to stop")
    print()
    import subprocess
    subprocess.run([sys.executable, "improved_trading_engine.py"])


def run_original_system():
    """Run original trading system"""
    print("\n📊 Starting Original Trading System...")
    print("Press Ctrl+C to stop")
    print()
    try:
        import subprocess
        subprocess.run([sys.executable, "btc_trading_main.py"])
    except FileNotFoundError:
        print("⚠️  Original btc_trading_main.py not found")
        print("Please ensure all original files are in the directory")


def create_config():
    """Create/edit configuration"""
    from config import SystemConfig, TradingConfig, RiskConfig, DataConfig
    
    print("\n⚙️  Configuration Creator")
    print("="*70)
    
    print("\n📊 Trading Parameters:")
    ema_fast = input(f"EMA Fast [20]: ").strip() or "20"
    ema_slow = input(f"EMA Slow [50]: ").strip() or "50"
    rsi_period = input(f"RSI Period [14]: ").strip() or "14"
    
    print("\n🛡️  Risk Management:")
    initial_capital = input(f"Initial Capital [10000]: ").strip() or "10000"
    max_risk = input(f"Max Risk Per Trade % [2.0]: ").strip() or "2.0"
    trailing_stop = input(f"Trailing Stop % [2.0]: ").strip() or "2.0"
    
    print("\n📡 Data Settings:")
    symbol = input(f"Symbol [btcusdt]: ").strip() or "btcusdt"
    
    print("\n🎯 Features:")
    use_fg = input(f"Enable Fear & Greed Index? [y/n] (y): ").strip().lower() or "y"
    use_risk = input(f"Enable Risk Management? [y/n] (y): ").strip().lower() or "y"
    
    # Create config
    config = SystemConfig(
        trading=TradingConfig(
            ema_fast=int(ema_fast),
            ema_slow=int(ema_slow),
            rsi_period=int(rsi_period)
        ),
        risk=RiskConfig(
            initial_capital=float(initial_capital),
            max_risk_per_trade_pct=float(max_risk),
            trailing_stop_pct=float(trailing_stop),
            use_trailing_stop=True
        ),
        data=DataConfig(
            symbol=symbol.lower()
        ),
        enable_fear_greed_index=(use_fg == 'y'),
        enable_risk_management=(use_risk == 'y')
    )
    
    # Save config
    filename = input("\nSave as [config.json]: ").strip() or "config.json"
    config.save_to_file(filename)
    
    print(f"\n✅ Configuration saved to {filename}")
    print(f"   Use this config by loading it in your scripts:")
    print(f"   config = SystemConfig.load_from_file('{filename}')")


def view_config():
    """View current configuration"""
    from config import SystemConfig
    import json
    
    print("\n📄 Current Configuration")
    print("="*70)
    
    try:
        config = SystemConfig.load_from_file("config.json")
        
        print("\n📊 Trading:")
        print(f"  EMA Fast: {config.trading.ema_fast}")
        print(f"  EMA Slow: {config.trading.ema_slow}")
        print(f"  RSI Period: {config.trading.rsi_period}")
        print(f"  RSI Overbought: {config.trading.rsi_overbought}")
        
        print("\n🛡️  Risk Management:")
        print(f"  Initial Capital: ${config.risk.initial_capital:,.2f}")
        print(f"  Max Risk Per Trade: {config.risk.max_risk_per_trade_pct}%")
        print(f"  Trailing Stop: {config.risk.trailing_stop_pct}%")
        print(f"  Use Trailing Stop: {config.risk.use_trailing_stop}")
        
        print("\n📡 Data:")
        print(f"  Symbol: {config.data.symbol.upper()}")
        print(f"  Interval: {config.data.interval}")
        
        print("\n🎯 Features:")
        print(f"  Fear & Greed Index: {'✅ Enabled' if config.enable_fear_greed_index else '❌ Disabled'}")
        print(f"  Risk Management: {'✅ Enabled' if config.enable_risk_management else '❌ Disabled'}")
        
    except FileNotFoundError:
        print("⚠️  No configuration file found (config.json)")
        print("   Create one using option 6")
    
    print("="*70)


def run_backtest():
    """Run backtest"""
    print("\n📈 Running Backtest...")
    print("This will fetch historical data and test the strategy")
    print()
    
    symbol = input("Symbol [btcusdt]: ").strip() or "btcusdt"
    interval = input("Interval [1h]: ").strip() or "1h"
    limit = input("Candles to fetch [1000]: ").strip() or "1000"
    
    import subprocess
    cmd = [
        sys.executable, "btc_backtest.py",
        "--symbol", symbol,
        "--interval", interval,
        "--limit", limit
    ]
    subprocess.run(cmd)


def optimize_parameters():
    """Run parameter optimization"""
    print("\n🔧 Parameter Optimization")
    print("="*70)
    print("\nOptimization Methods:")
    print("  1. Grid Search (thorough but slow)")
    print("  2. Random Search (faster)")
    print("  3. Genetic Algorithm (smart)")
    print()
    
    method_choice = input("Select method [1-3] (1): ").strip() or "1"
    methods = {"1": "grid", "2": "random", "3": "genetic"}
    method = methods.get(method_choice, "grid")
    
    print(f"\nRunning {method} optimization...")
    print("This may take several minutes...")
    print()
    
    import subprocess
    subprocess.run([sys.executable, "optimizer.py", "--method", method])


def main():
    """Main entry point"""
    print_banner()
    
    # Check if this is first run
    try:
        from config import SystemConfig
        SystemConfig.load_from_file("config.json")
    except FileNotFoundError:
        print("\n🎯 FIRST TIME SETUP")
        print("="*70)
        print("No configuration found. Let's create one!")
        print("="*70)
        input("\nPress Enter to continue...")
        create_config()
    
    while True:
        show_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye! Happy trading!")
            break
        
        elif choice == "1":
            test_positions()
        
        elif choice == "2":
            check_fear_greed()
        
        elif choice == "3":
            test_websocket()
        
        elif choice == "4":
            run_improved_engine()
        
        elif choice == "5":
            run_original_system()
        
        elif choice == "6":
            create_config()
        
        elif choice == "7":
            view_config()
        
        elif choice == "8":
            run_backtest()
        
        elif choice == "9":
            optimize_parameters()
        
        else:
            print("\n❌ Invalid choice. Please try again.")
        
        if choice != "0":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)

