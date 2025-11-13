"""
Fear and Greed Index Integration
=================================
Fetches and integrates the Bitcoin Fear and Greed Index into trading decisions
"""

import requests
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class FearGreedData:
    """Fear and Greed Index data structure"""
    value: int
    classification: str
    timestamp: datetime
    
    def is_extreme_fear(self) -> bool:
        """Check if in extreme fear (buying opportunity)"""
        return self.value < 25
    
    def is_fear(self) -> bool:
        """Check if in fear zone"""
        return 25 <= self.value < 45
    
    def is_neutral(self) -> bool:
        """Check if neutral"""
        return 45 <= self.value < 55
    
    def is_greed(self) -> bool:
        """Check if in greed zone"""
        return 55 <= self.value < 75
    
    def is_extreme_greed(self) -> bool:
        """Check if in extreme greed (selling opportunity)"""
        return self.value >= 75


class FearGreedIndexFetcher:
    """Fetch Fear and Greed Index data"""
    
    def __init__(self):
        self.api_url = "https://api.alternative.me/fng/"
        self.cache: Optional[FearGreedData] = None
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self.last_fetch: Optional[datetime] = None
        
    def fetch_current(self) -> Optional[FearGreedData]:
        """
        Fetch current Fear and Greed Index
        
        Returns:
            FearGreedData object or None if fetch fails
        """
        # Check cache first
        if self.cache and self.last_fetch:
            if datetime.now() - self.last_fetch < self.cache_duration:
                logger.debug("Returning cached Fear & Greed Index")
                return self.cache
        
        try:
            logger.info("Fetching Fear & Greed Index...")
            response = requests.get(self.api_url, params={'limit': 1}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data['metadata']['error'] is None and data['data']:
                latest = data['data'][0]
                
                fear_greed = FearGreedData(
                    value=int(latest['value']),
                    classification=latest['value_classification'],
                    timestamp=datetime.fromtimestamp(int(latest['timestamp']))
                )
                
                # Update cache
                self.cache = fear_greed
                self.last_fetch = datetime.now()
                
                logger.info(f"Fear & Greed Index: {fear_greed.value} ({fear_greed.classification})")
                return fear_greed
            
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
        
        return None
    
    def fetch_historical(self, days: int = 30) -> List[FearGreedData]:
        """
        Fetch historical Fear and Greed Index data
        
        Args:
            days: Number of days of historical data
            
        Returns:
            List of FearGreedData objects
        """
        try:
            logger.info(f"Fetching {days} days of Fear & Greed Index history...")
            response = requests.get(self.api_url, params={'limit': days}, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            historical_data = []
            
            if data['metadata']['error'] is None and data['data']:
                for item in data['data']:
                    fear_greed = FearGreedData(
                        value=int(item['value']),
                        classification=item['value_classification'],
                        timestamp=datetime.fromtimestamp(int(item['timestamp']))
                    )
                    historical_data.append(fear_greed)
                
                logger.info(f"Fetched {len(historical_data)} historical data points")
                return historical_data
            
        except Exception as e:
            logger.error(f"Error fetching historical Fear & Greed Index: {e}")
        
        return []
    
    async def stream_updates(self, callback, interval: int = 3600):
        """
        Stream Fear and Greed Index updates
        
        Args:
            callback: Async function to call with new data
            interval: Update interval in seconds (default: 1 hour)
        """
        logger.info(f"Starting Fear & Greed Index stream (updates every {interval}s)...")
        
        while True:
            try:
                data = self.fetch_current()
                if data:
                    await callback(data)
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("Fear & Greed Index stream cancelled")
                break
            except Exception as e:
                logger.error(f"Error in Fear & Greed Index stream: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry


class FearGreedSignalEnhancer:
    """Enhance trading signals with Fear and Greed Index"""
    
    def __init__(self, fetcher: FearGreedIndexFetcher):
        self.fetcher = fetcher
        
    def should_enhance_buy(self, fear_greed: FearGreedData) -> tuple[bool, str]:
        """
        Check if Fear & Greed Index enhances buy signal
        
        Returns:
            Tuple of (should_enhance, reason)
        """
        if fear_greed.is_extreme_fear():
            return True, f"Extreme Fear ({fear_greed.value}) - Strong buying opportunity!"
        elif fear_greed.is_fear():
            return True, f"Fear ({fear_greed.value}) - Good buying opportunity"
        elif fear_greed.is_neutral():
            return False, f"Neutral sentiment ({fear_greed.value})"
        else:
            return False, f"Greedy market ({fear_greed.value}) - Caution on buys"
    
    def should_enhance_sell(self, fear_greed: FearGreedData) -> tuple[bool, str]:
        """
        Check if Fear & Greed Index enhances sell signal
        
        Returns:
            Tuple of (should_enhance, reason)
        """
        if fear_greed.is_extreme_greed():
            return True, f"Extreme Greed ({fear_greed.value}) - Strong selling opportunity!"
        elif fear_greed.is_greed():
            return True, f"Greed ({fear_greed.value}) - Good selling opportunity"
        elif fear_greed.is_neutral():
            return False, f"Neutral sentiment ({fear_greed.value})"
        else:
            return False, f"Fearful market ({fear_greed.value}) - Hold positions"
    
    def get_signal_confidence(self, signal_type: str, fear_greed: FearGreedData) -> float:
        """
        Calculate signal confidence based on Fear & Greed Index
        
        Args:
            signal_type: 'BUY' or 'SELL'
            fear_greed: FearGreedData object
            
        Returns:
            Confidence multiplier (0.5 to 1.5)
        """
        if signal_type == 'BUY':
            if fear_greed.is_extreme_fear():
                return 1.5  # 50% confidence boost
            elif fear_greed.is_fear():
                return 1.2  # 20% confidence boost
            elif fear_greed.is_extreme_greed():
                return 0.5  # 50% confidence reduction
            elif fear_greed.is_greed():
                return 0.8  # 20% confidence reduction
            else:
                return 1.0  # No change
        
        elif signal_type == 'SELL':
            if fear_greed.is_extreme_greed():
                return 1.5  # 50% confidence boost
            elif fear_greed.is_greed():
                return 1.2  # 20% confidence boost
            elif fear_greed.is_extreme_fear():
                return 0.5  # 50% confidence reduction
            elif fear_greed.is_fear():
                return 0.8  # 20% confidence reduction
            else:
                return 1.0  # No change
        
        return 1.0


def get_market_sentiment_summary(fear_greed: FearGreedData) -> str:
    """Get a human-readable market sentiment summary"""
    
    emoji_map = {
        "Extreme Fear": "😱",
        "Fear": "😰",
        "Neutral": "😐",
        "Greed": "😄",
        "Extreme Greed": "🤑"
    }
    
    emoji = emoji_map.get(fear_greed.classification, "❓")
    
    summary = f"{emoji} Market Sentiment: {fear_greed.classification} ({fear_greed.value}/100)\n"
    
    if fear_greed.is_extreme_fear():
        summary += "💡 Strong contrarian buying opportunity - others are panicking!"
    elif fear_greed.is_fear():
        summary += "💡 Good time to consider buying - market is fearful"
    elif fear_greed.is_neutral():
        summary += "💡 Wait for clearer signals - market is balanced"
    elif fear_greed.is_greed():
        summary += "💡 Consider taking profits - market is greedy"
    elif fear_greed.is_extreme_greed():
        summary += "💡 Strong selling opportunity - euphoric market conditions!"
    
    return summary


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("BITCOIN FEAR & GREED INDEX")
    print("="*70)
    
    fetcher = FearGreedIndexFetcher()
    
    # Fetch current index
    current = fetcher.fetch_current()
    if current:
        print(f"\n{get_market_sentiment_summary(current)}")
        print(f"\nTimestamp: {current.timestamp}")
        
        # Test signal enhancement
        enhancer = FearGreedSignalEnhancer(fetcher)
        
        buy_enhance, buy_reason = enhancer.should_enhance_buy(current)
        print(f"\nBuy Signal Enhancement: {'✅ YES' if buy_enhance else '❌ NO'}")
        print(f"Reason: {buy_reason}")
        
        sell_enhance, sell_reason = enhancer.should_enhance_sell(current)
        print(f"\nSell Signal Enhancement: {'✅ YES' if sell_enhance else '❌ NO'}")
        print(f"Reason: {sell_reason}")
        
        print(f"\nBuy Confidence Multiplier: {enhancer.get_signal_confidence('BUY', current):.2f}x")
        print(f"Sell Confidence Multiplier: {enhancer.get_signal_confidence('SELL', current):.2f}x")
    
    # Fetch historical data
    print("\n" + "="*70)
    print("HISTORICAL DATA (Last 7 days)")
    print("="*70)
    
    historical = fetcher.fetch_historical(days=7)
    if historical:
        for data in historical[:7]:  # Show last 7 days
            print(f"{data.timestamp.strftime('%Y-%m-%d')}: {data.value:>2} - {data.classification}")
    
    print("="*70)

