"""
Multi-Source Data Fetcher
==========================
Fetch real-time and historical data from multiple sources:
- Binance
- CoinGecko
- CoinMarketCap (optional)
- Kraken (optional)

Aggregates data for better reliability and cross-validation
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import time

logger = logging.getLogger(__name__)


class BinanceDataFetcher:
    """Fetch data from Binance"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        
    def get_klines(self, symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 1000) -> pd.DataFrame:
        """
        Fetch historical klines/candlestick data
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles (max 1000)
        """
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol.upper(),
                'interval': interval,
                'limit': limit
            }
            
            logger.info(f"Fetching {limit} candles from Binance ({symbol}, {interval})")
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
            
            df['source'] = 'binance'
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✅ Binance: Fetched {len(df)} candles")
            return df[['open', 'high', 'low', 'close', 'volume', 'source']]
            
        except Exception as e:
            logger.error(f"❌ Binance fetch error: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str = "BTCUSDT") -> Optional[float]:
        """Get current price"""
        try:
            url = f"{self.base_url}/ticker/price"
            response = requests.get(url, params={'symbol': symbol.upper()}, timeout=5)
            response.raise_for_status()
            return float(response.json()['price'])
        except Exception as e:
            logger.error(f"Error fetching Binance price: {e}")
            return None


class CoinGeckoDataFetcher:
    """Fetch data from CoinGecko"""
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        
    def get_ohlc(self, coin_id: str = "bitcoin", vs_currency: str = "usd", days: int = 30) -> pd.DataFrame:
        """
        Fetch OHLC data from CoinGecko
        
        Args:
            coin_id: Coin ID (bitcoin, ethereum, etc.)
            vs_currency: Quote currency (usd, eur, etc.)
            days: Number of days (1, 7, 14, 30, 90, 180, 365, max)
        """
        try:
            url = f"{self.base_url}/coins/{coin_id}/ohlc"
            params = {
                'vs_currency': vs_currency,
                'days': days
            }
            
            logger.info(f"Fetching {days} days OHLC from CoinGecko ({coin_id})")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['volume'] = np.nan  # CoinGecko OHLC doesn't include volume
            df['source'] = 'coingecko'
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✅ CoinGecko: Fetched {len(df)} candles")
            return df
            
        except Exception as e:
            logger.error(f"❌ CoinGecko fetch error: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, coin_id: str = "bitcoin", vs_currency: str = "usd") -> Optional[float]:
        """Get current price"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': vs_currency
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return float(response.json()[coin_id][vs_currency])
        except Exception as e:
            logger.error(f"Error fetching CoinGecko price: {e}")
            return None
    
    def get_market_data(self, coin_id: str = "bitcoin") -> Dict:
        """Get comprehensive market data"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'community_data': 'false',
                'developer_data': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get('market_data', {})
            
            return {
                'current_price': market_data.get('current_price', {}).get('usd'),
                'market_cap': market_data.get('market_cap', {}).get('usd'),
                'total_volume': market_data.get('total_volume', {}).get('usd'),
                'price_change_24h': market_data.get('price_change_percentage_24h'),
                'price_change_7d': market_data.get('price_change_percentage_7d'),
                'price_change_30d': market_data.get('price_change_percentage_30d'),
                'ath': market_data.get('ath', {}).get('usd'),
                'ath_date': market_data.get('ath_date', {}).get('usd'),
                'atl': market_data.get('atl', {}).get('usd'),
                'atl_date': market_data.get('atl_date', {}).get('usd'),
                'circulating_supply': market_data.get('circulating_supply'),
                'max_supply': market_data.get('max_supply')
            }
            
        except Exception as e:
            logger.error(f"Error fetching CoinGecko market data: {e}")
            return {}


class KrakenDataFetcher:
    """Fetch data from Kraken (optional backup source)"""
    
    def __init__(self):
        self.base_url = "https://api.kraken.com/0/public"
        
    def get_ohlc(self, pair: str = "XBTUSD", interval: int = 60, since: Optional[int] = None) -> pd.DataFrame:
        """
        Fetch OHLC data from Kraken
        
        Args:
            pair: Trading pair (XBTUSD, ETHUSD, etc.)
            interval: Time interval in minutes (1, 5, 15, 30, 60, 240, 1440)
            since: Return data since this timestamp
        """
        try:
            url = f"{self.base_url}/OHLC"
            params = {
                'pair': pair,
                'interval': interval
            }
            if since:
                params['since'] = since
            
            logger.info(f"Fetching OHLC from Kraken ({pair}, {interval}m)")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('error'):
                logger.error(f"Kraken API error: {result['error']}")
                return pd.DataFrame()
            
            # Extract the pair data (key varies)
            pair_key = list(result['result'].keys())[0]
            data = result['result'][pair_key]
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df['source'] = 'kraken'
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"✅ Kraken: Fetched {len(df)} candles")
            return df[['open', 'high', 'low', 'close', 'volume', 'source']]
            
        except Exception as e:
            logger.error(f"❌ Kraken fetch error: {e}")
            return pd.DataFrame()


class MultiSourceDataAggregator:
    """Aggregate data from multiple sources for reliability"""
    
    def __init__(self):
        self.binance = BinanceDataFetcher()
        self.coingecko = CoinGeckoDataFetcher()
        self.kraken = KrakenDataFetcher()
        
    def get_comprehensive_data(self, 
                               symbol: str = "BTCUSDT",
                               interval: str = "1h",
                               days: int = 30,
                               sources: List[str] = ['binance', 'coingecko']) -> pd.DataFrame:
        """
        Fetch data from multiple sources and aggregate
        
        Args:
            symbol: Trading symbol
            interval: Time interval
            days: Number of days
            sources: List of sources to use
        """
        logger.info(f"📊 Fetching data from {len(sources)} sources...")
        
        dataframes = []
        
        # Fetch from Binance
        if 'binance' in sources:
            df_binance = self.binance.get_klines(symbol, interval, limit=min(days * 24, 1000))
            if not df_binance.empty:
                dataframes.append(df_binance)
        
        # Fetch from CoinGecko
        if 'coingecko' in sources:
            coin_id = self._symbol_to_coingecko_id(symbol)
            df_coingecko = self.coingecko.get_ohlc(coin_id, days=days)
            if not df_coingecko.empty:
                dataframes.append(df_coingecko)
        
        # Fetch from Kraken
        if 'kraken' in sources:
            pair = self._symbol_to_kraken_pair(symbol)
            interval_minutes = self._interval_to_minutes(interval)
            df_kraken = self.kraken.get_ohlc(pair, interval=interval_minutes)
            if not df_kraken.empty:
                dataframes.append(df_kraken)
        
        if not dataframes:
            logger.error("❌ No data fetched from any source")
            return pd.DataFrame()
        
        # Use primary source (Binance preferred)
        primary_df = dataframes[0].copy()
        
        logger.info(f"✅ Successfully fetched data from {len(dataframes)} source(s)")
        logger.info(f"📈 Total candles: {len(primary_df)}")
        logger.info(f"📅 Date range: {primary_df.index[0]} to {primary_df.index[-1]}")
        
        return primary_df
    
    def get_current_prices_from_all_sources(self, symbol: str = "BTCUSDT") -> Dict[str, float]:
        """Get current price from all sources for comparison"""
        prices = {}
        
        # Binance
        binance_price = self.binance.get_current_price(symbol)
        if binance_price:
            prices['binance'] = binance_price
        
        # CoinGecko
        coin_id = self._symbol_to_coingecko_id(symbol)
        coingecko_price = self.coingecko.get_current_price(coin_id)
        if coingecko_price:
            prices['coingecko'] = coingecko_price
        
        if prices:
            avg_price = np.mean(list(prices.values()))
            prices['average'] = avg_price
            
            # Calculate spread
            if len(prices) > 2:
                spread = (max(prices.values()) - min(prices.values())) / avg_price * 100
                prices['spread_pct'] = spread
        
        return prices
    
    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """Convert trading symbol to CoinGecko ID"""
        mapping = {
            'BTCUSDT': 'bitcoin',
            'ETHUSDT': 'ethereum',
            'BNBUSDT': 'binancecoin',
            'ADAUSDT': 'cardano',
            'DOGEUSDT': 'dogecoin',
            'XRPUSDT': 'ripple',
            'SOLUSDT': 'solana',
            'DOTUSDT': 'polkadot',
            'MATICUSDT': 'matic-network',
            'LINKUSDT': 'chainlink'
        }
        return mapping.get(symbol.upper(), 'bitcoin')
    
    def _symbol_to_kraken_pair(self, symbol: str) -> str:
        """Convert trading symbol to Kraken pair"""
        mapping = {
            'BTCUSDT': 'XBTUSD',
            'ETHUSDT': 'ETHUSD',
            'ADAUSDT': 'ADAUSD',
            'XRPUSDT': 'XRPUSD',
            'DOTUSDT': 'DOTUSD',
            'LINKUSDT': 'LINKUSD'
        }
        return mapping.get(symbol.upper(), 'XBTUSD')
    
    def _interval_to_minutes(self, interval: str) -> int:
        """Convert interval string to minutes"""
        mapping = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440
        }
        return mapping.get(interval, 60)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("MULTI-SOURCE DATA FETCHER")
    print("="*70)
    
    aggregator = MultiSourceDataAggregator()
    
    # Fetch comprehensive data
    print("\n📊 Fetching comprehensive data...")
    df = aggregator.get_comprehensive_data(
        symbol="BTCUSDT",
        interval="1h",
        days=30,
        sources=['binance', 'coingecko']
    )
    
    if not df.empty:
        print(f"\n✅ Data fetched successfully!")
        print(f"\nData preview:")
        print(df.head())
        print(f"\nData info:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Date range: {df.index[0]} to {df.index[-1]}")
    
    # Get current prices from all sources
    print("\n" + "="*70)
    print("CURRENT PRICES (Cross-Source Comparison)")
    print("="*70)
    
    prices = aggregator.get_current_prices_from_all_sources("BTCUSDT")
    
    for source, price in prices.items():
        if source == 'spread_pct':
            print(f"  Spread: {price:.4f}%")
        else:
            print(f"  {source.capitalize()}: ${price:,.2f}")
    
    # Get CoinGecko market data
    print("\n" + "="*70)
    print("COINGECKO MARKET DATA")
    print("="*70)
    
    market_data = aggregator.coingecko.get_market_data("bitcoin")
    
    for key, value in market_data.items():
        if value is not None:
            if 'price' in key or 'cap' in key or 'volume' in key or 'ath' in key or 'atl' in key:
                if isinstance(value, (int, float)):
                    print(f"  {key}: ${value:,.2f}")
                else:
                    print(f"  {key}: {value}")
            elif 'change' in key:
                print(f"  {key}: {value:.2f}%")
            else:
                print(f"  {key}: {value}")
    
    print("\n" + "="*70)

