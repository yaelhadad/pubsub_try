import requests
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

# Import shared components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import settings
from shared.models import NewsData

logger = logging.getLogger(__name__)

class FinnhubNewsFetcher:
    """
    Finnhub API client optimized for performance and reliability.
    
    Optimization techniques:
    1. Connection pooling with requests.Session
    2. Intelligent rate limiting
    3. Caching recent results
    4. Batch processing
    """
    
    def __init__(self):
        """Initialize with optimized session and caching."""
        # Optimization: Use session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'X-Finnhub-Token': settings.finnhub_api_key,
            'User-Agent': 'StockAlertSystem/1.0'
        })
        
        # Simple caching for optimization (avoid duplicate API calls)
        self.news_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        
        # Rate limiting - Finnhub allows 60 calls/minute
        self.last_call_time = 0
        self.min_call_interval = 1.0  # 1 second between calls
        
        # Performance metrics
        self.api_calls_count = 0
        self.cache_hits = 0
        
    def _rate_limit(self):
        """Implement rate limiting to avoid API quota issues."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def _get_cache_key(self, symbol: str, category: str) -> str:
        """Generate cache key for optimization."""
        return f"{symbol}:{category}:{int(time.time() / self.cache_ttl)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        return cache_key in self.news_cache
    
    def get_company_news(self, symbol: str, days_back: int = 1) -> List[NewsData]:
        """
        Fetch company news from Finnhub API.
        
        Optimization: Uses caching and rate limiting for better performance.
        """
        # Check cache first
        cache_key = self._get_cache_key(symbol, "company_news")
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for {symbol} company news")
            self.cache_hits += 1
            return self.news_cache[cache_key]
        
        try:
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            # Format dates for API
            from_str = from_date.strftime('%Y-%m-%d')
            to_str = to_date.strftime('%Y-%m-%d')
            
            # Rate limiting
            self._rate_limit()
            
            # Make API call
            url = "https://finnhub.io/api/v1/company-news"
            params = {
                'symbol': symbol,
                'from': from_str,
                'to': to_str
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            self.api_calls_count += 1
            
            # Process response
            news_data = response.json()
            
            # Convert to NewsData models
            news_list = []
            for article in news_data[:10]:  # Limit to top 10 for performance
                try:
                    news_item = NewsData(
                        headline=article.get('headline', ''),
                        summary=article.get('summary', ''),
                        url=article.get('url', ''),
                        datetime=article.get('datetime', 0),
                        source=article.get('source', '')
                    )
                    news_list.append(news_item)
                except Exception as e:
                    logger.warning(f"Error processing news item: {e}")
                    continue
            
            # Cache the results
            self.news_cache[cache_key] = news_list
            
            logger.info(f"Fetched {len(news_list)} news articles for {symbol}")
            return news_list
            
        except requests.RequestException as e:
            logger.error(f"Finnhub API request failed for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching news for {symbol}: {e}")
            return []
    
    def get_market_news(self, category: str = "general", limit: int = 20) -> List[NewsData]:
        """
        Fetch general market news from Finnhub.
        
        Optimization: Cached results to reduce API calls.
        """
        cache_key = self._get_cache_key("market", category)
        if self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for market news: {category}")
            self.cache_hits += 1
            return self.news_cache[cache_key]
        
        try:
            # Rate limiting
            self._rate_limit()
            
            # Make API call
            url = "https://finnhub.io/api/v1/news"
            params = {
                'category': category,
                'minId': 0
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            self.api_calls_count += 1
            
            # Process response
            news_data = response.json()
            
            # Convert to NewsData models
            news_list = []
            for article in news_data[:limit]:
                try:
                    news_item = NewsData(
                        headline=article.get('headline', ''),
                        summary=article.get('summary', ''),
                        url=article.get('url', ''),
                        datetime=article.get('datetime', 0),
                        source=article.get('source', '')
                    )
                    news_list.append(news_item)
                except Exception as e:
                    logger.warning(f"Error processing market news item: {e}")
                    continue
            
            # Cache the results
            self.news_cache[cache_key] = news_list
            
            logger.info(f"Fetched {len(news_list)} market news articles")
            return news_list
            
        except requests.RequestException as e:
            logger.error(f"Finnhub market news API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching market news: {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics for monitoring."""
        return {
            "api_calls_made": self.api_calls_count,
            "cache_hits": self.cache_hits,
            "cache_hit_ratio": self.cache_hits / max(self.api_calls_count, 1),
            "cached_items": len(self.news_cache)
        }

# Global instance for reuse (optimization)
finnhub_fetcher = FinnhubNewsFetcher() 