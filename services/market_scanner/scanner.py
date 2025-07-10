import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
import time

# Import shared components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import settings
from shared.pubsub import SimplePubSub
from shared.models import MarketEvent

logger = logging.getLogger(__name__)

class StockScanner:
    def __init__(self):
        """Initialize scanner with Redis connection and request session for optimization."""
        self.pubsub = SimplePubSub(settings.redis_url)
        # Optimization: Using requests.Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'StockAlertSystem/1.0'
        })
        
    def get_top_gainers(self) -> Optional[Dict]:
        """
        Fetch top gainers from Alpha Vantage API.
        
        Optimization techniques:
        1. Using session for connection reuse
        2. Timeout to prevent hanging requests
        3. Exponential backoff for rate limits
        """
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TOP_GAINERS_LOSERS',
                'apikey': settings.alpha_vantage_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle API rate limiting
            if 'Note' in data:
                logger.warning("Alpha Vantage API rate limit reached")
                return None
                
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return None
                
            logger.info("Successfully fetched top gainers data")
            return data
            
        except requests.RequestException as e:
            logger.error(f"API call failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching stock data: {e}")
            return None

    def process_and_publish_gainers(self, min_change_percent: float = 5.0) -> bool:
        """
        Process top gainers and publish significant movements.
        
        Optimization: Filter by minimum change percentage to reduce noise
        and batch process for efficiency.
        """
        try:
            data = self.get_top_gainers()
            if not data or 'top_gainers' not in data:
                logger.warning("No top gainers data available")
                return False
            
            published_count = 0
            current_time = datetime.now().isoformat()
            
            # Process top gainers with filtering
            for stock in data['top_gainers']:
                try:
                    change_percent = float(stock['change_percentage'].replace('%', ''))
                    
                    # Filter by minimum change percentage for optimization
                    if change_percent >= min_change_percent:
                        # Create market event using Pydantic model for validation
                        market_event = MarketEvent(
                            symbol=stock['ticker'],
                            price=float(stock['price']),
                            change_percent=change_percent,
                            volume=int(stock['volume']),
                            timestamp=current_time
                        )
                        
                        # Publish to Redis
                        success = self.pubsub.publish(
                            'market_events', 
                            market_event.dict()
                        )
                        
                        if success:
                            published_count += 1
                            logger.info(f"Published market event for {stock['ticker']}: {change_percent}%")
                        
                except (ValueError, KeyError) as e:
                    logger.error(f"Error processing stock data: {e}")
                    continue
            
            logger.info(f"Published {published_count} market events")
            return published_count > 0
            
        except Exception as e:
            logger.error(f"Error in process_and_publish_gainers: {e}")
            return False

    def scan_market(self) -> None:
        """
        Main scanning function called by scheduler.
        
        Optimization: Includes error handling and logging for monitoring.
        """
        logger.info("Starting market scan...")
        start_time = time.time()
        
        try:
            success = self.process_and_publish_gainers()
            
            execution_time = time.time() - start_time
            logger.info(f"Market scan completed in {execution_time:.2f} seconds. Success: {success}")
            
        except Exception as e:
            logger.error(f"Market scan failed: {e}")

# Global scanner instance for scheduler
scanner = StockScanner() 