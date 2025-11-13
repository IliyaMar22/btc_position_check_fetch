import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from scipy.stats import pearsonr, spearmanr, norm, skew, kurtosis
from scipy import stats
from fredapi import Fred
import requests
from bs4 import BeautifulSoup
import re
from typing import Tuple, Dict, List, Optional
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import Ridge, Lasso
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.offline import plot
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class UltraAdvancedCPIBitcoinAnalyzer:
    """
    Ultra-advanced analyzer for CPI release impact on Bitcoin with:
    - Advanced visualizations with custom styling
    - Sentiment analysis integration
    - Regime detection algorithms
    - Advanced risk metrics
    - Interactive dashboards
    - Machine learning ensemble models
    - Real-time market sentiment
    """
    
    def __init__(self, fred_api_key: str = "2eec5119549a63abd19a754bd819ca58", btc_quote: str = "USD"):
        """Initialize the ultra-advanced analyzer."""
        self.fred_api_key = fred_api_key.strip() if fred_api_key else None
        self.fred = Fred(api_key=self.fred_api_key) if self.fred_api_key else None
        
        # Data storage
        self.btc_data = None
        self.multi_asset_data = None
        self.cpi_releases = None
        self.analysis_results = None
        self.ml_models = {}
        self.monte_carlo_results = None
        self.sentiment_data = None
        
        # Preferred BTC quote currency (USD, EUR, USDT, USDC)
        self.btc_quote = btc_quote.upper()
        
        # Enhanced market regime parameters
        self.market_regimes = {
            'extreme_fear': {'base_vol': 0.08, 'trend_factor': -2.5, 'cpi_sensitivity': 3.0, 'color': '#FF4444'},
            'fear': {'base_vol': 0.06, 'trend_factor': -1.8, 'cpi_sensitivity': 2.0, 'color': '#FF6666'},
            'neutral': {'base_vol': 0.04, 'trend_factor': 0.1, 'cpi_sensitivity': 1.0, 'color': '#FFAA00'},
            'greed': {'base_vol': 0.03, 'trend_factor': 1.2, 'cpi_sensitivity': 0.8, 'color': '#66FF66'},
            'extreme_greed': {'base_vol': 0.05, 'trend_factor': 2.0, 'cpi_sensitivity': 0.6, 'color': '#00FF00'}
        }
        
        # Advanced technical indicators
        self.technical_indicators = {}
        
        # Risk metrics storage
        self.risk_metrics = {}
        
    def set_btc_quote(self, quote: str) -> None:
        """Set preferred BTC quote currency (e.g., USD, EUR, USDT, USDC)."""
        self.btc_quote = (quote or "USD").upper()

    def fetch_enhanced_multi_asset_data(self, start_date: str = "2019-09-01", end_date: str = None, btc_quote: str = None) -> Dict:
        """Fetch comprehensive multi-asset data with additional metrics."""
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if btc_quote:
            self.set_btc_quote(btc_quote)
            
        print("🌍 Fetching enhanced multi-asset data...")
        
        # Expanded asset universe
        assets = {
            # BTC base symbol decided below depending on quote currency
            'ETH-USD': 'Ethereum', 
            'GLD': 'Gold ETF',
            'SLV': 'Silver ETF',
            '^GSPC': 'S&P 500',
            '^IXIC': 'NASDAQ',
            '^RUT': 'Russell 2000',
            'DX-Y.NYB': 'Dollar Index',
            '^TNX': '10Y Treasury Yield',
            '^FVX': '5Y Treasury Yield',
            'TLT': '20+ Year Treasury Bond ETF',
            'IEF': '7-10 Year Treasury Bond ETF',
            '^VIX': 'VIX',
            '^GVZ': 'Gold VIX',
            'OIL': 'Crude Oil',
            'UNG': 'Natural Gas ETF',
            'DBA': 'Agriculture ETF',
            'REIT': 'Real Estate ETF',
            'ARKK': 'ARK Innovation ETF',
            'QQQ': 'NASDAQ 100 ETF'
        }
        
        multi_asset_data = {}
        
        # Decide BTC symbol for Yahoo Finance
        btc_symbol_map_yahoo = {
            'USD': 'BTC-USD',
            'EUR': 'BTC-EUR'
        }
        btc_symbol_yahoo = btc_symbol_map_yahoo.get(self.btc_quote, 'BTC-USD')
        # Insert BTC at the top
        assets = {btc_symbol_yahoo: f'Bitcoin ({self.btc_quote})', **assets}
        
        for symbol, name in assets.items():
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(start=start_date, end=end_date, interval="1d")
                
                if not data.empty:
                    # Ensure UTC timezone
                    if data.index.tz is None:
                        data.index = data.index.tz_localize('UTC')
                    else:
                        data.index = data.index.tz_convert('UTC')
                    
                    # Calculate additional metrics
                    data['Returns'] = data['Close'].pct_change() * 100
                    data['Log_Returns'] = np.log(data['Close'] / data['Close'].shift(1)) * 100
                    data['Volatility_20d'] = data['Returns'].rolling(20).std()
                    data['Volatility_5d'] = data['Returns'].rolling(5).std()
                    data['RSI_14'] = self._calculate_rsi(data['Close'], 14)
                    data['MACD'] = self._calculate_macd(data['Close'])
                    data['BB_Upper'], data['BB_Lower'] = self._calculate_bollinger_bands(data['Close'])
                    
                    multi_asset_data[symbol] = {
                        'name': name,
                        'data': data,
                        'returns': data['Returns'],
                        'log_returns': data['Log_Returns'],
                        'volatility_20d': data['Volatility_20d'],
                        'volatility_5d': data['Volatility_5d'],
                        'rsi': data['RSI_14'],
                        'macd': data['MACD'],
                        'bollinger_upper': data['BB_Upper'],
                        'bollinger_lower': data['BB_Lower']
                    }
                    print(f"✓ Fetched {name}: {len(data)} records")
                else:
                    # Fallback for BTC daily from Binance if Yahoo fails
                    if name.startswith('Bitcoin'):
                        daily_df = self._fetch_btc_from_binance(quote=self.btc_quote, interval='1d', start_date=start_date, end_date=end_date)
                        if daily_df is not None and not daily_df.empty:
                            daily_df['Returns'] = daily_df['Close'].pct_change() * 100
                            daily_df['Log_Returns'] = np.log(daily_df['Close'] / daily_df['Close'].shift(1)) * 100
                            daily_df['Volatility_20d'] = daily_df['Returns'].rolling(20).std()
                            daily_df['Volatility_5d'] = daily_df['Returns'].rolling(5).std()
                            daily_df['RSI_14'] = self._calculate_rsi(daily_df['Close'], 14)
                            daily_df['MACD'] = self._calculate_macd(daily_df['Close'])
                            daily_df['BB_Upper'], daily_df['BB_Lower'] = self._calculate_bollinger_bands(daily_df['Close'])
                            multi_asset_data[symbol] = {
                                'name': name,
                                'data': daily_df,
                                'returns': daily_df['Returns'],
                                'log_returns': daily_df['Log_Returns'],
                                'volatility_20d': daily_df['Volatility_20d'],
                                'volatility_5d': daily_df['Volatility_5d'],
                                'rsi': daily_df['RSI_14'],
                                'macd': daily_df['MACD'],
                                'bollinger_upper': daily_df['BB_Upper'],
                                'bollinger_lower': daily_df['BB_Lower']
                            }
                            print(f"✓ Fallback (Binance) fetched {name}: {len(daily_df)} records")
                        else:
                            print(f"✗ Failed to fetch {name}")
                    else:
                        print(f"✗ Failed to fetch {name}")
                    
            except Exception as e:
                print(f"✗ Error fetching {name}: {e}")
        
        # Fetch Bitcoin high-frequency data
        try:
            # Respect Yahoo 60-day window for 5m/15m
            now = datetime.now()
            recent_start_1h = (now - timedelta(days=90)).strftime("%Y-%m-%d")
            recent_start_60d = (now - timedelta(days=59)).strftime("%Y-%m-%d")
            btc_ticker = yf.Ticker("BTC-USD")
            
            # Get multiple timeframes
            for interval, name in [("1h", "Hourly"), ("15m", "15min"), ("5m", "5min")]:
                try:
                    start_for_interval = recent_start_1h if interval == '1h' else recent_start_60d
                    btc_data = btc_ticker.history(start=start_for_interval, end=end_date, interval=interval)
                    
                    if not btc_data.empty:
                        if btc_data.index.tz is None:
                            btc_data.index = btc_data.index.tz_localize('UTC')
                        else:
                            btc_data.index = btc_data.index.tz_convert('UTC')
                        
                        btc_data['Returns'] = btc_data['Close'].pct_change() * 100
                        key = f'BTC_{interval.upper()}'
                        multi_asset_data[key] = {
                            'name': f'Bitcoin {name}',
                            'data': btc_data,
                            'returns': btc_data['Returns']
                        }
                        print(f"✓ Fetched Bitcoin {name}: {len(btc_data)} records")
                    else:
                        # Fallback to Binance klines for intraday
                        hf_df = self._fetch_btc_from_binance(quote=self.btc_quote, interval=interval, start_date=start_for_interval, end_date=end_date)
                        if hf_df is not None and not hf_df.empty:
                            hf_df['Returns'] = hf_df['Close'].pct_change() * 100
                            key = f'BTC_{interval.upper()}'
                            multi_asset_data[key] = {
                                'name': f'Bitcoin {name}',
                                'data': hf_df,
                                'returns': hf_df['Returns']
                            }
                            print(f"✓ Fallback (Binance) fetched Bitcoin {name}: {len(hf_df)} records")
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Could not fetch Bitcoin high-frequency data: {e}")
        
        self.multi_asset_data = multi_asset_data
        return multi_asset_data

    def _fetch_btc_from_binance(self, quote: str = 'USDT', interval: str = '1d', start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Fetch BTC data from Binance as a fallback.
        Supports intervals: 1d, 1h, 15m, 5m.
        """
        try:
            symbol_map = {
                'USDT': 'BTCUSDT',
                'USDC': 'BTCUSDC',
                'EUR': 'BTCEUR',
                'USD': 'BTCUSDT'
            }
            binance_symbol = symbol_map.get(quote.upper(), 'BTCUSDT')
            interval_map = {
                '1d': '1d',
                '1h': '1h',
                '15m': '15m',
                '5m': '5m'
            }
            binance_interval = interval_map.get(interval, '1d')

            base_url = 'https://api.binance.com/api/v3/klines'
            params = {
                'symbol': binance_symbol,
                'interval': binance_interval,
                'limit': 1000
            }
            # Time bounds (ms since epoch)
            def to_ms(dt_str: str) -> int:
                dt = pd.to_datetime(dt_str)
                return int(dt.tz_localize('UTC').timestamp() * 1000)

            if start_date:
                params['startTime'] = to_ms(start_date)
            if end_date:
                params['endTime'] = to_ms(end_date)

            resp = requests.get(base_url, params=params, timeout=15)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not isinstance(data, list) or not data:
                return None

            # Parse klines
            cols = ['Open time','Open','High','Low','Close','Volume','Close time','Quote asset volume','Number of trades','Taker buy base asset volume','Taker buy quote asset volume','Ignore']
            df = pd.DataFrame(data, columns=cols)
            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms', utc=True)
            df = df.set_index('Open time')
            for c in ['Open','High','Low','Close','Volume']:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            df.index = df.index.tz_convert('UTC')
            df = df[['Open','High','Low','Close','Volume']]
            return df
        except Exception:
            return None
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def _calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band
    
    def fetch_enhanced_cpi_data(self) -> pd.DataFrame:
        """Fetch enhanced CPI data with market sentiment and expectations."""
        print("📊 Fetching enhanced CPI data...")
        
        # Get basic CPI data
        cpi_data = self.fetch_cpi_from_fred()
        
        if cpi_data is None or cpi_data.empty:
            print("  ⚠️ Failed to fetch CPI data, using enhanced simulated data")
            cpi_data = self.generate_enhanced_simulated_cpi_data()
        
        # Generate expectations with market sentiment
        expected_data = self.generate_enhanced_cpi_expectations(cpi_data)
        
        # Merge and enhance data
        cpi_releases = self.merge_enhanced_cpi_data(cpi_data, expected_data)
        
        # Add market sentiment context
        self.add_market_sentiment_context(cpi_releases)
        
        self.cpi_releases = cpi_releases
        return cpi_releases
    
    def generate_enhanced_simulated_cpi_data(self) -> pd.DataFrame:
        """Generate realistic simulated CPI data with regime changes."""
        print("  🎲 Generating enhanced simulated CPI data...")
        
        end_date = datetime.now()
        start_date = datetime(2010, 1, 1)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='MS')
        release_dates = [date + timedelta(days=12) for date in dates]
        release_dates = [self.adjust_to_business_day(date) for date in release_dates]
        
        np.random.seed(42)
        n_releases = len(release_dates)
        
        # Enhanced CPI simulation with multiple regimes
        cpi_values = []
        market_stress = []
        
        for i, date in enumerate(pd.to_datetime(release_dates)):
            # Ensure timezone consistency for comparison
            date_naive = date.tz_localize(None) if date.tz is not None else date
            
            # Define different economic regimes using naive timestamps
            if date_naive >= pd.Timestamp('2020-03-01') and date_naive <= pd.Timestamp('2020-08-01'):
                # COVID deflationary shock
                regime_mean = 0.2
                regime_std = 1.5
                stress_level = 0.9
            elif date_naive >= pd.Timestamp('2021-03-01') and date_naive <= pd.Timestamp('2022-12-01'):
                # Post-COVID inflation surge
                regime_mean = 7.2
                regime_std = 2.5
                stress_level = 0.8
            elif date_naive >= pd.Timestamp('2023-01-01'):
                # Disinflation with uncertainty
                regime_mean = 3.8 - (i * 0.08) if i > 36 else 3.8
                regime_std = 1.8
                stress_level = 0.6
            elif date_naive >= pd.Timestamp('2018-01-01') and date_naive <= pd.Timestamp('2019-12-01'):
                # Trade war period
                regime_mean = 2.1
                regime_std = 0.6
                stress_level = 0.4
            else:
                # Normal period
                regime_mean = 2.0
                regime_std = 0.8
                stress_level = 0.2
            
            # Add cyclical patterns
            cycle_factor = 0.3 * np.sin(2 * np.pi * i / 12)  # Annual cycle
            seasonal_factor = 0.2 * np.sin(2 * np.pi * date_naive.month / 12)  # Seasonal
            
            cpi_value = np.random.normal(regime_mean + cycle_factor + seasonal_factor, regime_std)
            cpi_values.append(max(cpi_value, -3.0))  # Floor at -3%
            market_stress.append(stress_level)
        
        result_df = pd.DataFrame({
            'date': [date - timedelta(days=45) for date in release_dates],
            'release_date': release_dates,
            'cpi_actual': cpi_values,
            'market_stress': market_stress
        })
        
        print(f"  ✅ Generated {len(result_df)} enhanced simulated CPI records")
        return result_df
    
    def generate_enhanced_cpi_expectations(self, cpi_data: pd.DataFrame) -> pd.DataFrame:
        """Generate sophisticated CPI expectations with multiple forecasting models."""
        if cpi_data is None or cpi_data.empty:
            return self.fetch_cpi_expectations()
        
        cpi_data_reset = cpi_data.reset_index(drop=True)
        np.random.seed(123)
        
        expected_values = []
        confidence_intervals = []
        
        for idx in range(len(cpi_data_reset)):
            if idx == 0:
                expected = 2.5
                confidence = 0.8
            else:
                # Multiple forecasting approaches
                prev_actual = cpi_data_reset.iloc[idx - 1]['cpi_actual']
                prev_expected = expected_values[-1] if expected_values else 2.5
                
                # Adaptive expectations with multiple factors
                momentum_weight = 0.4
                mean_reversion_weight = 0.3
                trend_weight = 0.2
                noise_weight = 0.1
                
                # Calculate trend
                if idx >= 3:
                    recent_trend = np.mean([cpi_data_reset.iloc[j]['cpi_actual'] 
                                          for j in range(max(0, idx-3), idx)])
                else:
                    recent_trend = prev_actual
                
                # Calculate mean reversion target
                long_term_mean = 2.5
                
                # Combine forecasts
                expected = (momentum_weight * prev_actual +
                           mean_reversion_weight * long_term_mean +
                           trend_weight * recent_trend +
                           noise_weight * np.random.normal(0, 0.2))
                
                # Dynamic confidence based on recent volatility
                recent_vol = np.std([cpi_data_reset.iloc[j]['cpi_actual'] 
                                   for j in range(max(0, idx-6), idx)]) if idx >= 6 else 0.5
                confidence = max(0.3, 1.0 - recent_vol / 2.0)
            
            expected_values.append(expected)
            confidence_intervals.append(confidence)
        
        result_df = cpi_data_reset[['release_date']].copy()
        result_df['cpi_expected'] = expected_values
        result_df['confidence'] = confidence_intervals
        return result_df
    
    def merge_enhanced_cpi_data(self, actual_data: pd.DataFrame, expected_data: pd.DataFrame) -> pd.DataFrame:
        """Merge CPI data with enhanced features."""
        merged = pd.merge(actual_data, expected_data, on='release_date', how='inner')
        
        # Basic surprise metrics
        merged['cpi_surprise'] = merged['cpi_actual'] - merged['cpi_expected']
        merged['cpi_surprise_abs'] = abs(merged['cpi_surprise'])
        merged['cpi_surprise_std'] = (merged['cpi_surprise'] - merged['cpi_surprise'].mean()) / merged['cpi_surprise'].std()
        
        # Enhanced surprise categories
        merged['surprise_magnitude'] = pd.cut(
            merged['cpi_surprise_abs'],
            bins=[0, 0.1, 0.3, 0.5, 1.0, float('inf')],
            labels=['tiny', 'small', 'medium', 'large', 'extreme']
        )
        
        # Sentiment classification
        merged['news_sentiment'] = merged['cpi_surprise'].apply(
            lambda x: 'very_negative' if x > 0.5 else 
                     'negative' if x > 0.2 else 
                     'positive' if x < -0.2 else 
                     'very_positive' if x < -0.5 else 'neutral'
        )
        
        # Market impact prediction
        merged['predicted_impact'] = merged['cpi_surprise'] * merged.get('market_stress', 0.5)
        
        # Time-based features
        merged['release_hour'] = pd.to_datetime(merged['release_date']).dt.hour
        merged['release_day_of_week'] = pd.to_datetime(merged['release_date']).dt.dayofweek
        merged['release_month'] = pd.to_datetime(merged['release_date']).dt.month
        merged['release_quarter'] = pd.to_datetime(merged['release_date']).dt.quarter
        
        merged = merged.sort_values('release_date').reset_index(drop=True)
        print(f"Created {len(merged)} enhanced CPI release events")
        
        return merged
    
    def add_market_sentiment_context(self, cpi_releases: pd.DataFrame):
        """Add market sentiment context to CPI releases."""
        if not self.multi_asset_data or '^VIX' not in self.multi_asset_data:
            return
        
        vix_data = self.multi_asset_data['^VIX']['data']
        
        for i, row in cpi_releases.iterrows():
            release_date = pd.to_datetime(row['release_date'])
            
            # Ensure timezone consistency
            if vix_data.index.tz is not None and release_date.tz is None:
                release_date = release_date.tz_localize('UTC')
            elif vix_data.index.tz is None and release_date.tz is not None:
                release_date = release_date.tz_localize(None)
            elif vix_data.index.tz is not None and release_date.tz is not None:
                release_date = release_date.tz_convert(vix_data.index.tz)
            
            # Get VIX level around release date
            vix_window = vix_data[
                (vix_data.index >= release_date - timedelta(days=5)) &
                (vix_data.index <= release_date + timedelta(days=1))
            ]
            
            if not vix_window.empty:
                avg_vix = vix_window['Close'].mean()
                vix_volatility = vix_window['Close'].std()
                
                cpi_releases.loc[i, 'vix_level'] = avg_vix
                cpi_releases.loc[i, 'vix_volatility'] = vix_volatility
                
                # Enhanced regime classification
                if avg_vix > 35:
                    cpi_releases.loc[i, 'market_regime'] = 'extreme_fear'
                elif avg_vix > 25:
                    cpi_releases.loc[i, 'market_regime'] = 'fear'
                elif avg_vix < 15:
                    cpi_releases.loc[i, 'market_regime'] = 'extreme_greed'
                elif avg_vix < 20:
                    cpi_releases.loc[i, 'market_regime'] = 'greed'
                else:
                    cpi_releases.loc[i, 'market_regime'] = 'neutral'
            else:
                cpi_releases.loc[i, 'vix_level'] = np.nan
                cpi_releases.loc[i, 'market_regime'] = 'unknown'
    
    def fetch_cpi_from_fred(self) -> pd.DataFrame:
        """Fetch CPI data from FRED API."""
        if not self.fred:
            print("  ⚠️ FRED API not available, using simulated data")
            return self.generate_enhanced_simulated_cpi_data()
        
        try:
            import ssl
            import urllib.request
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Monkey patch urllib to use our SSL context
            original_urlopen = urllib.request.urlopen
            urllib.request.urlopen = lambda *args, **kwargs: original_urlopen(*args, **kwargs, context=ssl_context)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5 * 365)
            
            cpi_series = self.fred.get_series('CPIAUCSL',
                                            start=start_date.strftime('%Y-%m-%d'),
                                            end=end_date.strftime('%Y-%m-%d'))
            
            # Restore original urlopen
            urllib.request.urlopen = original_urlopen
            
            cpi_df = pd.DataFrame({
                'date': cpi_series.index,
                'cpi_actual': cpi_series.values
            })
            
            cpi_df = cpi_df.sort_values('date')
            cpi_df['cpi_actual'] = cpi_df['cpi_actual'].pct_change(periods=12) * 100
            cpi_df = cpi_df.dropna()
            
            cpi_df['release_date'] = cpi_df['date'] + pd.DateOffset(days=45)
            cpi_df['release_date'] = cpi_df['release_date'].apply(self.adjust_to_business_day)
            
            print("  ✅ Successfully fetched CPI data from FRED")
            return cpi_df
            
        except Exception as e:
            print(f"  ⚠️ Error fetching FRED data: {e}")
            print("  🎲 Falling back to simulated CPI data...")
            return self.generate_enhanced_simulated_cpi_data()
    
    def fetch_cpi_expectations(self) -> pd.DataFrame:
        """Generate CPI expectations with realistic forecasting errors."""
        if hasattr(self, 'cpi_releases') and self.cpi_releases is not None:
            base_data = self.cpi_releases.copy()
        else:
            base_data = self.generate_enhanced_simulated_cpi_data()
        
        if base_data is None:
            base_data = self.generate_enhanced_simulated_cpi_data()
        
        np.random.seed(123)
        expected_values = []
        
        for i, row in base_data.iterrows():
            if i == 0:
                expected = 2.5
            else:
                prev_actual = base_data.iloc[i - 1]['cpi_actual']
                anchor_weight = 0.3
                momentum_weight = 0.4
                forecast_error = np.random.normal(0, 0.3)
                
                expected = (anchor_weight * 2.5 +
                           momentum_weight * prev_actual +
                           (1 - anchor_weight - momentum_weight) * expected_values[-1] +
                           forecast_error)
            
            expected_values.append(expected)
        
        base_data['cpi_expected'] = expected_values
        return base_data[['release_date', 'cpi_expected']]
    
    def adjust_to_business_day(self, date: datetime) -> datetime:
        """Adjust to business day with proper timezone."""
        # Convert to naive datetime for weekday calculation
        if hasattr(date, 'tz') and date.tz is not None:
            date_naive = date.tz_localize(None)
        else:
            date_naive = date
        
        # Adjust for weekend
        if date_naive.weekday() >= 5:
            days_to_add = 7 - date_naive.weekday()
            date_naive = date_naive + timedelta(days=days_to_add)
        
        # Set time to 13:30 UTC
        date_naive = date_naive.replace(hour=13, minute=30, second=0, microsecond=0)
        
        # Convert back to timezone-aware if original was timezone-aware
        if hasattr(date, 'tz') and date.tz is not None:
            return date_naive.tz_localize('UTC')
        else:
            return date_naive
    
    def analyze_enhanced_btc_reaction(self) -> pd.DataFrame:
        """Analyze Bitcoin price reactions with enhanced metrics."""
        print("🔍 Analyzing enhanced Bitcoin reactions to CPI releases...")
        
        if self.cpi_releases is None or not self.multi_asset_data:
            raise ValueError("Must fetch CPI and BTC data first")
        
        results = []
        btc_data = self.multi_asset_data.get('BTC-USD', {}).get('data')
        btc_hourly = self.multi_asset_data.get('BTC_1H', {}).get('data')
        btc_15min = self.multi_asset_data.get('BTC_15M', {}).get('data')
        
        if btc_data is None:
            raise ValueError("Bitcoin data not available")
        
        for _, cpi_row in self.cpi_releases.iterrows():
            release_datetime = pd.to_datetime(cpi_row['release_date'])
            
            # Get comprehensive BTC reaction
            btc_reaction = self.get_enhanced_btc_price_reaction(
                release_datetime, btc_data, btc_hourly, btc_15min
            )
            
            # Calculate additional metrics
            additional_metrics = self.calculate_advanced_metrics(
                btc_reaction, cpi_row, btc_data
            )
            
            # Combine all data
            result_row = {
                'date': cpi_row['release_date'],
                'cpi_expected': cpi_row['cpi_expected'],
                'cpi_actual': cpi_row['cpi_actual'],
                'cpi_surprise': cpi_row['cpi_surprise'],
                'news_sentiment': cpi_row['news_sentiment'],
                'surprise_magnitude': cpi_row['surprise_magnitude'],
                'market_regime': cpi_row.get('market_regime', 'unknown'),
                'vix_level': cpi_row.get('vix_level', np.nan),
                'confidence': cpi_row.get('confidence', np.nan),
                **btc_reaction,
                **additional_metrics
            }
            
            results.append(result_row)
        
        self.analysis_results = pd.DataFrame(results)
        
        # Debug: Print available columns
        print(f"  🔍 Available columns: {list(self.analysis_results.columns)}")
        
        # Check which columns are available for dropna
        available_columns = self.analysis_results.columns.tolist()
        dropna_columns = []
        
        if 'btc_price_before' in available_columns:
            dropna_columns.append('btc_price_before')
        
        # Check for any 15-minute price column
        for col in available_columns:
            if '15min' in col and 'price' in col and 'after' in col:
                dropna_columns.append(col)
                break
        
        # If no 15min column, use any available price column
        if not dropna_columns:
            for col in available_columns:
                if 'price' in col and 'before' in col:
                    dropna_columns.append(col)
                    break
        
        print(f"  🔍 Dropna columns: {dropna_columns}")
        
        if dropna_columns:
            self.analysis_results = self.analysis_results.dropna(subset=dropna_columns)
        else:
            print("  ⚠️ No price data columns found for filtering")
        
        print(f"Completed enhanced analysis for {len(self.analysis_results)} CPI releases")
        return self.analysis_results
    
    def get_enhanced_btc_price_reaction(self, release_datetime: pd.Timestamp, 
                                      btc_daily: pd.DataFrame, 
                                      btc_hourly: pd.DataFrame = None,
                                      btc_15min: pd.DataFrame = None) -> Dict:
        """Get comprehensive Bitcoin price reaction with multiple timeframes."""
        try:
            # Convert to same timezone if needed
            if release_datetime.tz is None:
                release_datetime = release_datetime.tz_localize('UTC')
            else:
                release_datetime = release_datetime.tz_convert('UTC')
            
            reaction_data = {}
            
            # Try 15-minute data first for precision
            if btc_15min is not None and not btc_15min.empty:
                reaction_data.update(self._get_precise_reaction(btc_15min, release_datetime, '15min'))
            
            # Try hourly data
            if btc_hourly is not None and not btc_hourly.empty:
                reaction_data.update(self._get_precise_reaction(btc_hourly, release_datetime, '1h'))
            
            # Fall back to daily data
            if not reaction_data or all(v is None for v in reaction_data.values()):
                reaction_data.update(self._get_daily_reaction(btc_daily, release_datetime))
            
            return reaction_data
            
        except Exception as e:
            print(f"Error getting BTC reaction for {release_datetime}: {e}")
            return self._empty_enhanced_reaction()
    
    def _get_precise_reaction(self, data: pd.DataFrame, release_time: pd.Timestamp, timeframe: str) -> Dict:
        """Get precise price reaction from high-frequency data."""
        # Find closest time before release
        before_data = data[data.index < release_time]
        after_data = data[data.index >= release_time]
        
        if before_data.empty or after_data.empty:
            return {}
        
        price_before = before_data['Close'].iloc[-1]
        
        # Get prices at different intervals after release
        intervals = {
            '5min': 5, '10min': 10, '15min': 15, '30min': 30, 
            '1h': 60, '2h': 120, '4h': 240, '6h': 360, '12h': 720, '24h': 1440
        }
        
        reaction = {'btc_price_before': price_before}
        
        for interval_name, minutes in intervals.items():
            if timeframe == '15min':
                # For 15-minute data, calculate exact intervals
                target_time = release_time + timedelta(minutes=minutes)
                after_target = data[data.index >= target_time]
            else:
                # For hourly data, approximate
                hours_needed = minutes / 60
                after_target = after_data.head(max(1, int(hours_needed)))
            
            if not after_target.empty:
                price_after = after_target['Close'].iloc[0]
                return_pct = (price_after - price_before) / price_before * 100
                
                reaction[f'btc_price_{interval_name}_after'] = price_after
                reaction[f'btc_return_{interval_name}'] = return_pct
        
        return reaction
    
    def _get_daily_reaction(self, data: pd.DataFrame, release_time: pd.Timestamp) -> Dict:
        """Get daily reaction as fallback."""
        release_date = release_time.date()
        
        # Find closest trading day
        daily_dates = [idx.date() for idx in data.index]
        date_diffs = [(abs((d - release_date).days), i) for i, d in enumerate(daily_dates)]
        
        if not date_diffs:
            return {}
        
        min_diff_days, closest_idx = min(date_diffs)
        
        if min_diff_days <= 3:  # Within 3 days
            day_data = data.iloc[closest_idx]
            
            return {
                'btc_price_before': day_data['Open'],
                'btc_price_15min_after': (day_data['Open'] + day_data['High']) / 2,
                'btc_price_1h_after': day_data['High'],
                'btc_price_2h_after': day_data['Close'],
                'btc_price_4h_after': day_data['Close'],
                'btc_price_24h_after': day_data['Close'],
                'btc_return_15min': ((day_data['High'] + day_data['Open']) / 2 - day_data['Open']) / day_data['Open'] * 100,
                'btc_return_1h': (day_data['High'] - day_data['Open']) / day_data['Open'] * 100,
                'btc_return_2h': (day_data['Close'] - day_data['Open']) / day_data['Open'] * 100,
                'btc_return_4h': (day_data['Close'] - day_data['Open']) / day_data['Open'] * 100,
                'btc_return_24h': (day_data['Close'] - day_data['Open']) / day_data['Open'] * 100
            }
        
        return {}
    
    def _empty_enhanced_reaction(self) -> Dict:
        """Return empty enhanced reaction dictionary."""
        intervals = ['5min', '10min', '15min', '30min', '1h', '2h', '4h', '6h', '12h', '24h']
        
        reaction = {'btc_price_before': None}
        for interval in intervals:
            reaction[f'btc_price_{interval}_after'] = None
            reaction[f'btc_return_{interval}'] = None
        
        return reaction
    
    def calculate_advanced_metrics(self, btc_reaction: Dict, cpi_row: pd.Series, btc_data: pd.DataFrame) -> Dict:
        """Calculate advanced financial metrics."""
        metrics = {}
        
        # Volatility metrics
        if 'btc_return_15min' in btc_reaction and btc_reaction['btc_return_15min'] is not None:
            # Calculate realized volatility
            recent_returns = btc_data['Returns'].dropna().tail(20)
            if len(recent_returns) > 0:
                metrics['realized_volatility_20d'] = recent_returns.std()
                metrics['volatility_percentile'] = stats.percentileofscore(
                    recent_returns, btc_reaction['btc_return_15min']
                )
        
        # Risk metrics
        if 'btc_return_15min' in btc_reaction and btc_reaction['btc_return_15min'] is not None:
            return_15m = btc_reaction['btc_return_15min']
            
            # Sharpe ratio approximation
            if 'realized_volatility_20d' in metrics and metrics['realized_volatility_20d'] > 0:
                metrics['sharpe_ratio_15m'] = return_15m / metrics['realized_volatility_20d']
            
            # Risk-adjusted return
            metrics['risk_adjusted_return'] = return_15m / (1 + abs(return_15m))
            
            # Momentum indicators
            if 'btc_return_1h' in btc_reaction and btc_reaction['btc_return_1h'] is not None:
                metrics['momentum_continuation'] = (
                    btc_reaction['btc_return_1h'] * btc_reaction['btc_return_15min']
                ) > 0
        
        # Market regime impact
        if 'market_regime' in cpi_row and cpi_row['market_regime'] in self.market_regimes:
            regime_params = self.market_regimes[cpi_row['market_regime']]
            metrics['regime_expected_volatility'] = regime_params['base_vol']
            metrics['regime_cpi_sensitivity'] = regime_params['cpi_sensitivity']
        
        # Surprise impact analysis
        if 'cpi_surprise' in cpi_row:
            surprise = cpi_row['cpi_surprise']
            metrics['surprise_impact_ratio'] = (
                btc_reaction.get('btc_return_15min', 0) / surprise if surprise != 0 else 0
            )
            metrics['surprise_efficiency'] = abs(metrics['surprise_impact_ratio'])
        
        return metrics
    
    def run_enhanced_monte_carlo_simulation(self, n_simulations: int = 2000) -> Dict:
        """Run enhanced Monte Carlo simulation with multiple scenarios."""
        print(f"🎯 Running enhanced Monte Carlo simulation with {n_simulations} iterations...")
        
        if self.cpi_releases is None:
            raise ValueError("Must fetch CPI data first")
        
        # Get historical data for calibration
        cpi_surprises = self.cpi_releases['cpi_surprise'].dropna()
        surprise_mean = cpi_surprises.mean()
        surprise_std = cpi_surprises.std()
        surprise_skew = skew(cpi_surprises)
        surprise_kurt = kurtosis(cpi_surprises)
        
        simulation_results = {}
        
        for regime_name, params in self.market_regimes.items():
            print(f"  📈 Simulating {regime_name.upper()} market regime...")
            
            regime_results = []
            
            for sim in range(n_simulations):
                # Generate realistic CPI surprise with historical distribution
                cpi_surprise = self._generate_realistic_cpi_surprise(
                    surprise_mean, surprise_std, surprise_skew, surprise_kurt
                )
                
                # Generate Bitcoin return with regime-specific parameters
                btc_return = self._generate_regime_btc_return(cpi_surprise, params)
                
                # Additional scenario analysis
                scenarios = self._generate_scenario_analysis(cpi_surprise, params)
                
                regime_results.append({
                    'simulation': sim,
                    'cpi_surprise': cpi_surprise,
                    'btc_return_15m': btc_return,
                    'regime': regime_name,
                    **scenarios
                })
            
            simulation_results[regime_name] = pd.DataFrame(regime_results)
        
        # Calculate comprehensive statistics
        regime_stats = self._calculate_comprehensive_statistics(simulation_results)
        
        self.monte_carlo_results = {
            'simulations': simulation_results,
            'statistics': regime_stats,
            'parameters': self.market_regimes,
            'historical_params': {
                'surprise_mean': surprise_mean,
                'surprise_std': surprise_std,
                'surprise_skew': surprise_skew,
                'surprise_kurt': surprise_kurt
            }
        }
        
        print("✅ Enhanced Monte Carlo simulation completed!")
        return self.monte_carlo_results
    
    def _generate_realistic_cpi_surprise(self, mean, std, skew, kurt):
        """Generate realistic CPI surprise using Johnson SU distribution."""
        # Use Box-Muller transformation with skew and kurtosis adjustments
        u1, u2 = np.random.uniform(0, 1, 2)
        z = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
        
        # Apply skewness and kurtosis
        if skew != 0:
            z = z + skew * (z**2 - 1) / 6
        if kurt != 0:
            z = z + kurt * (z**3 - 3*z) / 24
        
        return mean + std * z
    
    def _generate_regime_btc_return(self, cpi_surprise, regime_params):
        """Generate Bitcoin return based on regime and CPI surprise."""
        # Base return from regime
        base_return = np.random.normal(
            regime_params['trend_factor'] * 0.1,
            regime_params['base_vol']
        )
        
        # CPI impact
        cpi_impact = -cpi_surprise * regime_params['cpi_sensitivity'] * 0.5
        
        # Regime-specific noise
        noise = np.random.normal(0, regime_params['base_vol'] * 0.3)
        
        # Volatility clustering (GARCH-like effect)
        vol_cluster = np.random.normal(0, regime_params['base_vol'] * 0.2)
        
        return base_return + cpi_impact + noise + vol_cluster
    
    def _generate_scenario_analysis(self, cpi_surprise, regime_params):
        """Generate additional scenario analysis."""
        scenarios = {}
        
        # Stress scenarios
        scenarios['stress_scenario'] = cpi_surprise * 1.5
        scenarios['mild_scenario'] = cpi_surprise * 0.5
        
        # Regime persistence
        scenarios['regime_persistence'] = np.random.beta(2, 2)  # Beta distribution for persistence
        
        # Market microstructure effects
        scenarios['liquidity_impact'] = np.random.normal(0, 0.1)
        scenarios['sentiment_impact'] = np.random.normal(0, 0.15)
        
        return scenarios
    
    def _calculate_comprehensive_statistics(self, simulation_results):
        """Calculate comprehensive statistics for each regime."""
        regime_stats = {}
        
        for regime, data in simulation_results.items():
            returns = data['btc_return_15m']
            
            stats = {
                'mean_return': returns.mean(),
                'std_return': returns.std(),
                'skewness': skew(returns),
                'kurtosis': kurtosis(returns),
                'sharpe_ratio': returns.mean() / returns.std() if returns.std() > 0 else 0,
                'var_95': returns.quantile(0.05),
                'var_99': returns.quantile(0.01),
                'cvar_95': returns[returns <= returns.quantile(0.05)].mean(),
                'cvar_99': returns[returns <= returns.quantile(0.01)].mean(),
                'max_drawdown': self._calculate_max_drawdown(returns),
                'positive_return_prob': (returns > 0).mean(),
                'extreme_positive_prob': (returns > 2 * returns.std()).mean(),
                'extreme_negative_prob': (returns < -2 * returns.std()).mean(),
                'correlation_with_cpi': data['cpi_surprise'].corr(returns),
                'tail_dependence': self._calculate_tail_dependence(data['cpi_surprise'], returns)
            }
            
            regime_stats[regime] = stats
        
        return regime_stats
    
    def _calculate_max_drawdown(self, returns):
        """Calculate maximum drawdown."""
        cumulative = (1 + returns / 100).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min() * 100
    
    def _calculate_tail_dependence(self, x, y):
        """Calculate tail dependence coefficient."""
        # Simplified tail dependence calculation
        n = len(x)
        threshold = 0.1  # 10% threshold
        
        x_thresh = x.quantile(1 - threshold)
        y_thresh = y.quantile(1 - threshold)
        
        upper_tail = ((x >= x_thresh) & (y >= y_thresh)).sum()
        total_upper = (x >= x_thresh).sum()
        
        if total_upper > 0:
            return upper_tail / total_upper
        return 0
    
    def build_ensemble_ml_models(self) -> Dict:
        """Build ensemble machine learning models for prediction."""
        print("🤖 Building ensemble ML models...")
        
        if self.analysis_results is None:
            print("⚠️ Need to run analysis first")
            return {}
        
        # Prepare features
        clean_data = self.analysis_results.dropna(subset=['cpi_surprise', 'btc_return_15min'])
        
        if len(clean_data) < 30:
            print("⚠️ Insufficient data for ML models")
            return {}
        
        # Enhanced feature engineering
        features, targets, feature_names = self._prepare_enhanced_features(clean_data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, targets, test_size=0.3, random_state=42
        )
        
        # Scale features
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models
        models = {
            'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=200, max_depth=8, random_state=42),
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=0.1)
        }
        
        model_results = {}
        
        for name, model in models.items():
            print(f"  Training {name}...")
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred_train = model.predict(X_train_scaled)
            y_pred_test = model.predict(X_test_scaled)
            
            # Calculate metrics
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
            test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            test_mae = mean_absolute_error(y_test, y_pred_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            
            model_results[name] = {
                'model': model,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_rmse': train_rmse,
                'test_rmse': test_rmse,
                'test_mae': test_mae,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'predictions': {
                    'y_test': y_test,
                    'y_pred': y_pred_test
                }
            }
            
            print(f"    {name} - Test R²: {test_r2:.3f}, RMSE: {test_rmse:.3f}%")
        
        # Feature importance for tree-based models
        feature_importance = self._calculate_feature_importance(models, feature_names)
        
        # Ensemble prediction
        ensemble_pred = self._create_ensemble_prediction(models, X_test_scaled)
        ensemble_r2 = r2_score(y_test, ensemble_pred)
        ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
        
        self.ml_models = {
            'models': model_results,
            'scaler': scaler,
            'feature_names': feature_names,
            'feature_importance': feature_importance,
            'ensemble': {
                'predictions': ensemble_pred,
                'r2': ensemble_r2,
                'rmse': ensemble_rmse
            }
        }
        
        print(f"✅ Ensemble ML models completed! Best R²: {max([m['test_r2'] for m in model_results.values()]):.3f}")
        return self.ml_models

    def build_trade_action_classifier(self) -> Optional[Dict]:
        """Train a trade action classifier (long/short/hold)."""
        if self.analysis_results is None or self.analysis_results.empty:
            print("⚠️ No analysis data for trade classifier")
            return None
        df = self.analysis_results.dropna(subset=['btc_return_15min', 'cpi_surprise'])
        if len(df) < 30:
            print("⚠️ Insufficient events for trade classifier")
            return None
        ret_std = df['btc_return_15min'].std()
        hold_band = max(0.15, min(0.5, float(ret_std) * 0.25))
        def label_row(r):
            if r['btc_return_15min'] >= hold_band:
                return 'long'
            if r['btc_return_15min'] <= -hold_band:
                return 'short'
            return 'hold'
        df['action_label'] = df.apply(label_row, axis=1)
        X, _, feature_names = self._prepare_enhanced_features(df)
        y_cls = df['action_label'].values
        if self.ml_models and 'scaler' in self.ml_models:
            scaler = self.ml_models['scaler']
            X_scaled = scaler.transform(X)
        else:
            scaler = RobustScaler()
            X_scaled = scaler.fit_transform(X)
        clf = RandomForestClassifier(n_estimators=300, max_depth=12, class_weight='balanced', random_state=42)
        clf.fit(X_scaled, y_cls)
        proba = clf.predict_proba(X_scaled)
        conf = float(proba.max(axis=1).mean())
        self.trade_classifier = {
            'model': clf,
            'scaler': scaler,
            'feature_names': feature_names,
            'hold_band': hold_band,
            'avg_train_confidence': conf
        }
        print(f"✅ Trade classifier trained. Avg confidence: {conf:.2f}; hold band: ±{hold_band:.2f}%")
        return self.trade_classifier

    def predict_trade_actions(self) -> Optional[pd.DataFrame]:
        """Predict long/short/hold with confidence for each CPI event."""
        if self.trade_classifier is None:
            if self.build_trade_action_classifier() is None:
                return None
        if self.analysis_results is None or self.analysis_results.empty:
            return None
        df = self.analysis_results.copy()
        X, _, _ = self._prepare_enhanced_features(df)
        scaler = self.trade_classifier['scaler']
        clf = self.trade_classifier['model']
        Xs = scaler.transform(X)
        preds = clf.predict(Xs)
        proba = clf.predict_proba(Xs)
        classes = list(clf.classes_)
        df['trade_action'] = preds
        df['trade_confidence'] = proba.max(axis=1)
        for i, c in enumerate(classes):
            df[f'prob_{c}'] = proba[:, i]
        self.analysis_results = df
        return df

    def _scenario_params_from_regime(self, regime: str) -> Dict[str, float]:
        if self.monte_carlo_results and 'statistics' in self.monte_carlo_results and regime in self.monte_carlo_results['statistics']:
            stats_reg = self.monte_carlo_results['statistics'][regime]
            std = max(0.2, float(stats_reg.get('std_return', 1.0)))
        else:
            std = 1.0
        return {'long_thresh': +0.30 * std, 'short_thresh': -0.30 * std, 'base_target_mult': 0.75 * std, 'aggr_target_mult': 1.25 * std}

    def generate_trade_scenarios(self) -> Optional[pd.DataFrame]:
        if self.analysis_results is None or self.analysis_results.empty:
            return None
        if 'trade_action' not in self.analysis_results.columns:
            self.predict_trade_actions()
        rows = []
        for _, r in self.analysis_results.iterrows():
            price = r.get('btc_price_before', np.nan)
            if pd.isna(price):
                continue
            regime = r.get('market_regime', 'neutral')
            params = self._scenario_params_from_regime(regime)
            vol = r.get('realized_volatility_20d', 1.0)
            vol = float(1.0 if pd.isna(vol) else max(0.2, min(5.0, vol)))
            action = r.get('trade_action', 'hold')
            conf = float(r.get('trade_confidence', 0.5))
            dir_mult = 1 if action == 'long' else (-1 if action == 'short' else 0)
            scenarios = []
            for kind, risk_mult, target_mult in [('conservative', 0.5, 0.5 * params['base_target_mult']), ('base', 1.0, params['base_target_mult']), ('aggressive', 1.5, params['aggr_target_mult'])]:
                if dir_mult == 0:
                    entry = price
                    stop = price * (1 - 0.005)
                    target = price * (1 + 0.005)
                else:
                    entry = price
                    stop_pct = risk_mult * vol / 100.0
                    tgt_pct = target_mult / 100.0
                    if action == 'long':
                        stop = entry * (1 - stop_pct)
                        target = entry * (1 + tgt_pct)
                    else:
                        stop = entry * (1 + stop_pct)
                        target = entry * (1 - tgt_pct)
                rr = abs((target - entry) / (entry - stop)) if entry != stop else np.nan
                scenarios.append({'scenario': kind, 'action': action, 'confidence': conf, 'entry': entry, 'stop': stop, 'target': target, 'rr': rr})
            base = [s for s in scenarios if s['scenario'] == 'base'][0]
            out = {'date': r['date'], 'action': action, 'confidence': conf, 'entry': base['entry'], 'stop': base['stop'], 'target': base['target'], 'rr': base['rr'], 'scenario_conservative': scenarios[0], 'scenario_base': base, 'scenario_aggressive': scenarios[2]}
            rows.append(out)
        self.trade_scenarios = pd.DataFrame(rows)
        return self.trade_scenarios
    
    def _prepare_enhanced_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare enhanced features for ML models."""
        features = []
        targets = []
        
        for i, row in data.iterrows():
            feature_vector = [
                row['cpi_surprise'],
                abs(row['cpi_surprise']),
                row['cpi_actual'],
                row['cpi_expected'],
                row.get('vix_level', 20),
                row.get('confidence', 0.5),
            ]
            
            # Sentiment features
            sentiment_map = {'very_negative': -2, 'negative': -1, 'neutral': 0, 
                           'positive': 1, 'very_positive': 2}
            feature_vector.append(sentiment_map.get(row['news_sentiment'], 0))
            
            # Surprise magnitude features
            magnitude_map = {'tiny': 1, 'small': 2, 'medium': 3, 'large': 4, 'extreme': 5}
            feature_vector.append(magnitude_map.get(row['surprise_magnitude'], 3))
            
            # Market regime features
            regime_map = {'extreme_fear': -2, 'fear': -1, 'neutral': 0, 
                         'greed': 1, 'extreme_greed': 2}
            feature_vector.append(regime_map.get(row.get('market_regime', 'neutral'), 0))
            
            # Time-based features
            date = pd.to_datetime(row['date'])
            feature_vector.extend([
                date.hour,
                date.weekday(),
                date.month,
                date.quarter,
                date.day,
                date.isocalendar()[1]  # Week number
            ])
            
            # Technical indicators if available
            if 'realized_volatility_20d' in row and not pd.isna(row['realized_volatility_20d']):
                feature_vector.append(row['realized_volatility_20d'])
            else:
                feature_vector.append(2.0)  # Default volatility
            
            if 'volatility_percentile' in row and not pd.isna(row['volatility_percentile']):
                feature_vector.append(row['volatility_percentile'])
            else:
                feature_vector.append(50.0)  # Default percentile
            
            # Interaction features
            feature_vector.append(row['cpi_surprise'] * row.get('vix_level', 20))
            feature_vector.append(row['cpi_surprise'] * row.get('confidence', 0.5))
            
            features.append(feature_vector)
            targets.append(row['btc_return_15min'])
        
        feature_names = [
            'CPI_Surprise', 'CPI_Surprise_Abs', 'CPI_Actual', 'CPI_Expected',
            'VIX_Level', 'Confidence', 'Sentiment', 'Surprise_Magnitude',
            'Market_Regime', 'Hour', 'Weekday', 'Month', 'Quarter', 'Day', 'Week',
            'Realized_Vol_20d', 'Vol_Percentile', 'CPI_VIX_Interaction', 'CPI_Conf_Interaction'
        ]
        
        return np.array(features), np.array(targets), feature_names
    
    def _calculate_feature_importance(self, models: Dict, feature_names: List[str]) -> pd.DataFrame:
        """Calculate feature importance across models."""
        importance_data = []
        
        for name, model in models.items():
            if hasattr(model, 'feature_importances_'):
                for i, importance in enumerate(model.feature_importances_):
                    importance_data.append({
                        'model': name,
                        'feature': feature_names[i],
                        'importance': importance
                    })
        
        if importance_data:
            importance_df = pd.DataFrame(importance_data)
            avg_importance = importance_df.groupby('feature')['importance'].mean().sort_values(ascending=False)
            return avg_importance
        else:
            return pd.Series()
    
    def _create_ensemble_prediction(self, models: Dict, X_test: np.ndarray) -> np.ndarray:
        """Create ensemble prediction from multiple models."""
        predictions = []
        
        for name, model in models.items():
            pred = model.predict(X_test)
            predictions.append(pred)
        
        # Weighted average (can be optimized)
        weights = [0.3, 0.3, 0.2, 0.2]  # RandomForest, GradientBoosting, Ridge, Lasso
        ensemble_pred = np.average(predictions, axis=0, weights=weights)
        
        return ensemble_pred
    
    def create_ultra_advanced_visualizations(self) -> None:
        """Create ultra-advanced visualizations with custom styling."""
        print("📊 Creating ultra-advanced visualizations...")
        
        # Set up the plotting style
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
        
        # Create comprehensive dashboard
        fig = plt.figure(figsize=(20, 24))
        gs = GridSpec(6, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Monte Carlo Distribution Analysis
        ax1 = fig.add_subplot(gs[0, :2])
        self._plot_monte_carlo_distributions(ax1)
        
        # 2. CPI Surprise vs BTC Return Scatter
        ax2 = fig.add_subplot(gs[0, 2])
        self._plot_cpi_btc_scatter(ax2)
        
        # 3. Multi-timeframe BTC Returns
        ax3 = fig.add_subplot(gs[1, :2])
        self._plot_multi_timeframe_returns(ax3)
        
        # 4. Market Regime Analysis
        ax4 = fig.add_subplot(gs[1, 2])
        self._plot_market_regime_analysis(ax4)
        
        # 5. Risk Metrics Heatmap
        ax5 = fig.add_subplot(gs[2, :2])
        self._plot_risk_metrics_heatmap(ax5)
        
        # 6. ML Model Performance
        ax6 = fig.add_subplot(gs[2, 2])
        self._plot_ml_model_performance(ax6)
        
        # 7. Volatility Analysis
        ax7 = fig.add_subplot(gs[3, :2])
        self._plot_volatility_analysis(ax7)
        
        # 8. Feature Importance
        ax8 = fig.add_subplot(gs[3, 2])
        self._plot_feature_importance(ax8)
        
        # 9. Time Series Analysis
        ax9 = fig.add_subplot(gs[4, :])
        self._plot_time_series_analysis(ax9)
        
        # 10. Correlation Matrix
        ax10 = fig.add_subplot(gs[5, :])
        self._plot_correlation_matrix(ax10)
        
        # Add main title
        fig.suptitle('🚀 Ultra-Advanced CPI-Bitcoin Analysis Dashboard', 
                    fontsize=20, fontweight='bold', y=0.98)
        
        # Save the plot
        plt.savefig('ultra_advanced_cpi_analysis.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.show()
        
        # Create interactive Plotly dashboard
        self._create_interactive_dashboard()
        
        print("✅ Ultra-advanced visualizations created and saved!")
    
    def _plot_monte_carlo_distributions(self, ax):
        """Plot Monte Carlo simulation distributions."""
        if not self.monte_carlo_results:
            ax.text(0.5, 0.5, 'No Monte Carlo data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        
        for i, (regime, data) in enumerate(self.monte_carlo_results['simulations'].items()):
            returns = data['btc_return_15m']
            
            # Create histogram with KDE
            n, bins, patches = ax.hist(returns, bins=50, alpha=0.6, 
                                     color=colors[i % len(colors)], 
                                     label=f'{regime.replace("_", " ").title()}',
                                     density=True)
            
            # Add KDE curve
            from scipy.stats import gaussian_kde
            kde = gaussian_kde(returns)
            x_range = np.linspace(returns.min(), returns.max(), 200)
            ax.plot(x_range, kde(x_range), color=colors[i % len(colors)], 
                   linewidth=2, alpha=0.8)
        
        ax.set_xlabel('Bitcoin 15-minute Return (%)')
        ax.set_ylabel('Density')
        ax.set_title('Monte Carlo: BTC Return Distributions by Market Regime')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_cpi_btc_scatter(self, ax):
        """Plot CPI surprise vs BTC return scatter plot."""
        if self.analysis_results is None:
            ax.text(0.5, 0.5, 'No analysis data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        clean_data = self.analysis_results.dropna(subset=['cpi_surprise', 'btc_return_15min'])
        
        # Color by market regime
        regime_colors = {
            'extreme_fear': '#FF4444', 'fear': '#FF6666', 'neutral': '#FFAA00',
            'greed': '#66FF66', 'extreme_greed': '#00FF00'
        }
        
        for regime in clean_data['market_regime'].unique():
            if pd.isna(regime):
                continue
            regime_data = clean_data[clean_data['market_regime'] == regime]
            color = regime_colors.get(regime, '#888888')
            
            ax.scatter(regime_data['cpi_surprise'], regime_data['btc_return_15min'],
                      c=color, alpha=0.7, s=60, label=regime.replace('_', ' ').title())
        
        # Add trend line
        if len(clean_data) > 1:
            z = np.polyfit(clean_data['cpi_surprise'], clean_data['btc_return_15min'], 1)
            p = np.poly1d(z)
            ax.plot(clean_data['cpi_surprise'], p(clean_data['cpi_surprise']), 
                   "r--", alpha=0.8, linewidth=2)
        
        ax.set_xlabel('CPI Surprise (%)')
        ax.set_ylabel('BTC 15-min Return (%)')
        ax.set_title('CPI Surprise vs BTC Return')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
    
    def _plot_multi_timeframe_returns(self, ax):
        """Plot multi-timeframe BTC returns."""
        if self.analysis_results is None:
            ax.text(0.5, 0.5, 'No analysis data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        timeframes = ['btc_return_15min', 'btc_return_1h', 'btc_return_2h', 
                     'btc_return_4h', 'btc_return_24h']
        
        clean_data = self.analysis_results.dropna(subset=timeframes)
        
        if clean_data.empty:
            ax.text(0.5, 0.5, 'No multi-timeframe data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Create box plot
        data_to_plot = [clean_data[col].dropna() for col in timeframes]
        labels = ['15min', '1h', '2h', '4h', '24h']
        
        bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
        
        # Color the boxes
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_ylabel('Bitcoin Return (%)')
        ax.set_title('Multi-timeframe BTC Returns Distribution')
        ax.grid(True, alpha=0.3)
    
    def _plot_market_regime_analysis(self, ax):
        """Plot market regime analysis."""
        if self.analysis_results is None:
            ax.text(0.5, 0.5, 'No analysis data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        clean_data = self.analysis_results.dropna(subset=['market_regime', 'btc_return_15min'])
        
        if clean_data.empty:
            ax.text(0.5, 0.5, 'No regime data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Group by regime and calculate statistics
        regime_stats = clean_data.groupby('market_regime')['btc_return_15min'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).round(3)
        
        # Create bar plot
        regimes = regime_stats.index
        means = regime_stats['mean']
        stds = regime_stats['std']
        
        colors = ['#FF4444', '#FF6666', '#FFAA00', '#66FF66', '#00FF00']
        regime_colors = {regime: colors[i % len(colors)] for i, regime in enumerate(regimes)}
        
        bars = ax.bar(regimes, means, yerr=stds, capsize=5, 
                     color=[regime_colors[r] for r in regimes], alpha=0.7)
        
        ax.set_ylabel('Average BTC Return (%)')
        ax.set_title('BTC Performance by Market Regime')
        ax.set_xticklabels([r.replace('_', '\n').title() for r in regimes], rotation=45)
        ax.grid(True, alpha=0.3)
    
    def _plot_risk_metrics_heatmap(self, ax):
        """Plot risk metrics heatmap."""
        if not self.monte_carlo_results:
            ax.text(0.5, 0.5, 'No Monte Carlo data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Prepare data for heatmap
        regimes = list(self.monte_carlo_results['statistics'].keys())
        metrics = ['mean_return', 'std_return', 'sharpe_ratio', 'var_95', 'var_99', 'max_drawdown']
        
        heatmap_data = []
        for regime in regimes:
            stats = self.monte_carlo_results['statistics'][regime]
            row = [stats[metric] for metric in metrics]
            heatmap_data.append(row)
        
        heatmap_data = np.array(heatmap_data)
        
        # Normalize data for better visualization
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        heatmap_data_norm = scaler.fit_transform(heatmap_data)
        
        im = ax.imshow(heatmap_data_norm, cmap='RdYlBu_r', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics], rotation=45)
        ax.set_yticks(range(len(regimes)))
        ax.set_yticklabels([r.replace('_', ' ').title() for r in regimes])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Normalized Value')
        
        ax.set_title('Risk Metrics Heatmap by Market Regime')
    
    def _plot_ml_model_performance(self, ax):
        """Plot ML model performance comparison."""
        if not self.ml_models or 'models' not in self.ml_models:
            ax.text(0.5, 0.5, 'No ML model data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        models = list(self.ml_models['models'].keys())
        r2_scores = [self.ml_models['models'][m]['test_r2'] for m in models]
        rmse_scores = [self.ml_models['models'][m]['test_rmse'] for m in models]
        
        x = np.arange(len(models))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, r2_scores, width, label='R² Score', alpha=0.8, color='#4ECDC4')
        ax2 = ax.twinx()
        bars2 = ax2.bar(x + width/2, rmse_scores, width, label='RMSE (%)', alpha=0.8, color='#FF6B6B')
        
        ax.set_xlabel('Models')
        ax.set_ylabel('R² Score', color='#4ECDC4')
        ax2.set_ylabel('RMSE (%)', color='#FF6B6B')
        ax.set_title('ML Model Performance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.3f}', ha='center', va='bottom')
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{height:.2f}', ha='center', va='bottom')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_volatility_analysis(self, ax):
        """Plot volatility analysis."""
        if self.analysis_results is None:
            ax.text(0.5, 0.5, 'No analysis data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        clean_data = self.analysis_results.dropna(subset=['btc_return_15min'])
        
        if 'realized_volatility_20d' in clean_data.columns:
            # Plot volatility over time
            dates = pd.to_datetime(clean_data['date'])
            ax.scatter(dates, clean_data['realized_volatility_20d'], 
                      c=clean_data['btc_return_15min'], cmap='RdYlGn', 
                      alpha=0.7, s=60)
            
            ax.set_xlabel('Date')
            ax.set_ylabel('Realized Volatility (20d)')
            ax.set_title('Volatility Analysis Over Time')
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax.text(0.5, 0.5, 'No volatility data available', 
                   ha='center', va='center', transform=ax.transAxes)
        
        ax.grid(True, alpha=0.3)
    
    def _plot_feature_importance(self, ax):
        """Plot feature importance from ML models."""
        if not self.ml_models or 'feature_importance' not in self.ml_models:
            ax.text(0.5, 0.5, 'No feature importance data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        importance = self.ml_models['feature_importance']
        
        if importance.empty:
            ax.text(0.5, 0.5, 'No feature importance data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Plot top 10 features
        top_features = importance.head(10)
        
        bars = ax.barh(range(len(top_features)), top_features.values, 
                      color='#45B7D1', alpha=0.8)
        
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels([f.replace('_', ' ') for f in top_features.index])
        ax.set_xlabel('Feature Importance')
        ax.set_title('Top 10 Feature Importance')
        ax.grid(True, alpha=0.3)
    
    def _plot_time_series_analysis(self, ax):
        """Plot time series analysis."""
        if self.analysis_results is None:
            ax.text(0.5, 0.5, 'No analysis data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        clean_data = self.analysis_results.dropna(subset=['btc_return_15min', 'cpi_surprise'])
        
        if clean_data.empty:
            ax.text(0.5, 0.5, 'No time series data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        dates = pd.to_datetime(clean_data['date'])
        
        # Plot CPI surprise and BTC returns
        ax2 = ax.twinx()
        
        line1 = ax.plot(dates, clean_data['cpi_surprise'], 'o-', color='#FF6B6B', 
                       alpha=0.7, linewidth=2, markersize=4, label='CPI Surprise')
        line2 = ax2.plot(dates, clean_data['btc_return_15min'], 's-', color='#4ECDC4', 
                        alpha=0.7, linewidth=2, markersize=4, label='BTC Return')
        
        ax.set_xlabel('Date')
        ax.set_ylabel('CPI Surprise (%)', color='#FF6B6B')
        ax2.set_ylabel('BTC 15-min Return (%)', color='#4ECDC4')
        ax.set_title('Time Series: CPI Surprise vs BTC Returns')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_correlation_matrix(self, ax):
        """Plot correlation matrix."""
        if self.analysis_results is None:
            ax.text(0.5, 0.5, 'No analysis data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Select numeric columns for correlation
        numeric_cols = self.analysis_results.select_dtypes(include=[np.number]).columns
        correlation_data = self.analysis_results[numeric_cols].corr()
        
        # Create heatmap
        im = ax.imshow(correlation_data, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(correlation_data.columns)))
        ax.set_yticks(range(len(correlation_data.columns)))
        ax.set_xticklabels([col.replace('_', ' ').title() for col in correlation_data.columns], 
                          rotation=45, ha='right')
        ax.set_yticklabels([col.replace('_', ' ').title() for col in correlation_data.columns])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Correlation Coefficient')
        
        ax.set_title('Correlation Matrix: All Variables')
    
    def _create_interactive_dashboard(self):
        """Create interactive Plotly dashboard."""
        # Guard against ambiguous DataFrame truthiness
        if self.monte_carlo_results is None:
            print("⚠️ Insufficient data for interactive dashboard (no Monte Carlo results)")
            return
        if self.analysis_results is None or self.analysis_results.empty:
            print("⚠️ Insufficient data for interactive dashboard (no analysis results)")
            return
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Monte Carlo: BTC Returns by Market Regime',
                'CPI Surprise vs BTC Return (Interactive)',
                'Multi-Asset Correlation Heatmap',
                'ML Model Performance Comparison',
                'Risk Metrics Dashboard',
                'Time Series Analysis'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Monte Carlo Results
        for regime, data in self.monte_carlo_results['simulations'].items():
            fig.add_trace(
                go.Histogram(
                    x=data['btc_return_15m'],
                    name=f'{regime.replace("_", " ").title()}',
                    opacity=0.7,
                    nbinsx=50
                ),
                row=1, col=1
            )
        
        # 2. CPI vs BTC Scatter
        clean_data = self.analysis_results.dropna(subset=['cpi_surprise', 'btc_return_15min'])
        
        fig.add_trace(
            go.Scatter(
                x=clean_data['cpi_surprise'],
                y=clean_data['btc_return_15min'],
                mode='markers',
                name='Historical Events',
                marker=dict(
                    size=8,
                    color=clean_data['btc_return_15min'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="BTC Return %")
                ),
                text=[f"Date: {date}<br>Regime: {regime}<br>Surprise: {surprise:.2f}%<br>Return: {ret:.2f}%"
                      for date, regime, surprise, ret in zip(
                          clean_data['date'], clean_data['market_regime'],
                          clean_data['cpi_surprise'], clean_data['btc_return_15min']
                      )],
                hovertemplate='%{text}<extra></extra>'
            ),
            row=1, col=2
        )
        
        # 3. Risk Metrics
        if self.monte_carlo_results:
            regimes = list(self.monte_carlo_results['statistics'].keys())
            metrics = ['mean_return', 'std_return', 'sharpe_ratio', 'var_95']
            
            for metric in metrics:
                values = [self.monte_carlo_results['statistics'][r][metric] for r in regimes]
                fig.add_trace(
                    go.Bar(
                        x=regimes,
                        y=values,
                        name=metric.replace('_', ' ').title()
                    ),
                    row=2, col=1
                )
        
        # Update layout
        fig.update_layout(
            height=1200,
            title_text="🚀 Ultra-Advanced CPI-Bitcoin Interactive Dashboard",
            showlegend=True,
            template="plotly_white"
        )
        
        # Save interactive dashboard
        fig.write_html("ultra_advanced_cpi_dashboard.html")
        print("📊 Interactive dashboard saved as 'ultra_advanced_cpi_dashboard.html'")
    
    def run_ultra_comprehensive_analysis(self) -> Dict:
        """Run the complete ultra-advanced analysis pipeline."""
        print("🚀 Starting Ultra-Comprehensive CPI-Bitcoin Analysis...")
        print("=" * 70)
        
        results = {}
        
        try:
            # Step 1: Fetch enhanced multi-asset data
            print("\n1️⃣ Fetching enhanced multi-asset market data...")
            multi_asset_data = self.fetch_enhanced_multi_asset_data()
            results['multi_asset_data'] = multi_asset_data
            
            # Step 2: Fetch enhanced CPI data
            print("\n2️⃣ Fetching enhanced CPI data with market context...")
            cpi_data = self.fetch_enhanced_cpi_data()
            results['cpi_data'] = cpi_data
            
            # Step 3: Enhanced Bitcoin reaction analysis
            print("\n3️⃣ Analyzing enhanced Bitcoin reactions...")
            btc_analysis = self.analyze_enhanced_btc_reaction()
            results['btc_analysis'] = btc_analysis
            
            # Step 4: Enhanced Monte Carlo simulation
            print("\n4️⃣ Running enhanced Monte Carlo simulation...")
            monte_carlo_results = self.run_enhanced_monte_carlo_simulation(n_simulations=2000)
            results['monte_carlo'] = monte_carlo_results
            
            # Step 5: Ensemble ML models
            print("\n5️⃣ Building ensemble ML models...")
            ml_results = self.build_ensemble_ml_models()
            results['ml_models'] = ml_results
            
            # Step 6: Trade classifier and scenarios
            print("\n6️⃣ Building trade classifier and scenarios...")
            self.build_trade_action_classifier()
            self.predict_trade_actions()
            scenarios_df = self.generate_trade_scenarios()
            results['trade_scenarios'] = scenarios_df
            
            # Step 7: Ultra-advanced visualizations
            print("\n7️⃣ Creating ultra-advanced visualizations...")
            self.create_ultra_advanced_visualizations()
            
            # Step 8: Generate comprehensive insights
            print("\n8️⃣ Generating ultra-comprehensive insights...")
            insights = self.generate_ultra_comprehensive_insights(results)
            results['insights'] = insights
            
            print("\n" + insights)
            print("\n✅ Ultra-comprehensive analysis completed successfully!")
            print("=" * 70)
            
            return results
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def generate_ultra_comprehensive_insights(self, results: Dict) -> str:
        """Generate ultra-comprehensive insights from all analyses."""
        insights = []
        insights.append("🎯 ULTRA-COMPREHENSIVE CPI-BITCOIN ANALYSIS INSIGHTS")
        insights.append("=" * 70)
        
        # Basic statistics
        if 'btc_analysis' in results and results['btc_analysis'] is not None:
            clean_data = results['btc_analysis'].dropna(subset=['cpi_surprise', 'btc_return_15min'])
            
            insights.append(f"\n📊 ENHANCED STATISTICS:")
            insights.append(f"• Analysis Period: {clean_data['date'].min()} to {clean_data['date'].max()}")
            insights.append(f"• Total CPI Events: {len(clean_data)}")
            insights.append(f"• Average CPI Surprise: {clean_data['cpi_surprise'].mean():.3f}%")
            insights.append(f"• Average BTC 15m Return: {clean_data['btc_return_15min'].mean():.3f}%")
            insights.append(f"• BTC Return Volatility: {clean_data['btc_return_15min'].std():.3f}%")
            insights.append(f"• CPI-BTC Correlation: {clean_data['cpi_surprise'].corr(clean_data['btc_return_15min']):.3f}")
            
            # Advanced metrics
            if 'realized_volatility_20d' in clean_data.columns:
                avg_vol = clean_data['realized_volatility_20d'].mean()
                insights.append(f"• Average Realized Volatility (20d): {avg_vol:.3f}%")
            
            if 'sharpe_ratio_15m' in clean_data.columns:
                avg_sharpe = clean_data['sharpe_ratio_15m'].mean()
                insights.append(f"• Average Sharpe Ratio (15m): {avg_sharpe:.3f}")
        
        # Monte Carlo insights
        if 'monte_carlo' in results and results['monte_carlo']:
            mc_stats = results['monte_carlo']['statistics']
            insights.append(f"\n🎲 ENHANCED MONTE CARLO INSIGHTS:")
            
            for regime, stats in mc_stats.items():
                insights.append(f"\n  {regime.replace('_', ' ').upper()} Market:")
                insights.append(f"    • Expected Return: {stats['mean_return']:.3f}%")
                insights.append(f"    • Volatility: {stats['std_return']:.3f}%")
                insights.append(f"    • Sharpe Ratio: {stats['sharpe_ratio']:.3f}")
                insights.append(f"    • 95% VaR: {stats['var_95']:.3f}%")
                insights.append(f"    • 99% VaR: {stats['var_99']:.3f}%")
                insights.append(f"    • Max Drawdown: {stats['max_drawdown']:.3f}%")
                insights.append(f"    • CPI Correlation: {stats['correlation_with_cpi']:.3f}")
                insights.append(f"    • Win Probability: {stats['positive_return_prob']:.1%}")
                insights.append(f"    • Extreme Events: {stats['extreme_positive_prob']:.1%} pos, {stats['extreme_negative_prob']:.1%} neg")
        
        # ML Model insights
        if 'ml_models' in results and results['ml_models']:
            ml_results = results['ml_models']
            insights.append(f"\n🤖 ENSEMBLE ML MODEL INSIGHTS:")
            
            if 'ensemble' in ml_results:
                insights.append(f"• Ensemble R²: {ml_results['ensemble']['r2']:.3f}")
                insights.append(f"• Ensemble RMSE: {ml_results['ensemble']['rmse']:.3f}%")
            
            if 'models' in ml_results:
                best_model = max(ml_results['models'].items(), key=lambda x: x[1]['test_r2'])
                insights.append(f"• Best Model: {best_model[0]} (R²: {best_model[1]['test_r2']:.3f})")
                
                insights.append(f"\n📈 INDIVIDUAL MODEL PERFORMANCE:")
                for name, model_stats in ml_results['models'].items():
                    insights.append(f"  {name}: R²={model_stats['test_r2']:.3f}, RMSE={model_stats['test_rmse']:.3f}%")
            
            if 'feature_importance' in ml_results and not ml_results['feature_importance'].empty:
                insights.append(f"\n🔍 TOP PREDICTIVE FEATURES:")
                for i, (feature, importance) in enumerate(ml_results['feature_importance'].head(5).items()):
                    insights.append(f"  {i+1}. {feature.replace('_', ' ').title()}: {importance:.3f}")
        
        # Trading strategy recommendations
        insights.append(f"\n💡 ULTRA-ADVANCED TRADING STRATEGY RECOMMENDATIONS:")
        
        if 'monte_carlo' in results and results['monte_carlo']:
            best_regime = max(results['monte_carlo']['statistics'].items(),
                            key=lambda x: x[1]['sharpe_ratio'])
            worst_regime = min(results['monte_carlo']['statistics'].items(),
                             key=lambda x: x[1]['sharpe_ratio'])
            
            insights.append(f"• Best Risk-Adjusted Performance: {best_regime[0].replace('_', ' ').title()}")
            insights.append(f"  (Sharpe: {best_regime[1]['sharpe_ratio']:.3f}, Return: {best_regime[1]['mean_return']:.2f}%)")
            insights.append(f"• Highest Risk: {worst_regime[0].replace('_', ' ').title()}")
            insights.append(f"  (95% VaR: {worst_regime[1]['var_95']:.2f}%, Max DD: {worst_regime[1]['max_drawdown']:.2f}%)")
        
        insights.append(f"• Position Sizing: Use regime-specific volatility for optimal sizing")
        insights.append(f"• Risk Management: Monitor VIX levels for regime identification")
        insights.append(f"• Entry Timing: Higher CPI surprises generally correlate with negative BTC returns")
        insights.append(f"• Exit Strategy: Consider 2-4 hour holding periods based on momentum")
        insights.append(f"• Diversification: Monitor correlation with traditional assets")
        
        return '\n'.join(insights)


def main():
    """Main execution function for ultra-advanced analysis."""
    print("🚀 Ultra-Advanced CPI-Bitcoin Analysis Tool")
    print("==========================================")
    print("This ultra-advanced tool includes:")
    print("• Enhanced multi-asset correlation analysis")
    print("• Advanced Monte Carlo simulation with 5 market regimes")
    print("• Ensemble machine learning models")
    print("• Ultra-sophisticated visualizations")
    print("• Comprehensive risk metrics and insights")
    print("• Interactive dashboards")
    print("• Real-time market sentiment integration\n")
    
    # Initialize ultra-advanced analyzer
    analyzer = UltraAdvancedCPIBitcoinAnalyzer()
    
    try:
        # Run ultra-comprehensive analysis
        results = analyzer.run_ultra_comprehensive_analysis()
        
        # Additional ultra-advanced analyses
        print("\n🔥 ULTRA-ADVANCED BONUS ANALYSES:")
        
        # Risk analysis
        if results.get('monte_carlo'):
            print("\n📊 Ultra-Advanced Risk Analysis:")
            for regime, stats in results['monte_carlo']['statistics'].items():
                print(f"{regime.replace('_', ' ').title()} Market:")
                print(f"  Expected: {stats['mean_return']:.2f}%, Vol: {stats['std_return']:.2f}%")
                print(f"  Sharpe: {stats['sharpe_ratio']:.3f}, 95% VaR: {stats['var_95']:.2f}%")
                print(f"  Max DD: {stats['max_drawdown']:.2f}%, Win Rate: {stats['positive_return_prob']:.1%}")
                print()
        
        # Best/Worst scenarios
        if results.get('btc_analysis') is not None:
            clean_data = results['btc_analysis'].dropna(subset=['cpi_surprise', 'btc_return_15min'])
            
            print(f"🎯 Historical Extremes Analysis:")
            best_day = clean_data.loc[clean_data['btc_return_15min'].idxmax()]
            worst_day = clean_data.loc[clean_data['btc_return_15min'].idxmin()]
            
            print(f"Best BTC Performance: {best_day['btc_return_15min']:.2f}%")
            print(f"  (CPI surprise: {best_day['cpi_surprise']:.2f}%, Regime: {best_day['market_regime']})")
            print(f"Worst BTC Performance: {worst_day['btc_return_15min']:.2f}%")
            print(f"  (CPI surprise: {worst_day['cpi_surprise']:.2f}%, Regime: {worst_day['market_regime']})")
        
        print(f"\n🎉 Ultra-advanced analysis complete! Files generated:")
        print("   • ultra_advanced_cpi_analysis.png - Comprehensive static dashboard")
        print("   • ultra_advanced_cpi_dashboard.html - Interactive dashboard")
        print("   • All data saved in analyzer object for further analysis")
        
        return results
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
