import logging
import time
from datetime import datetime
from typing import Dict, Any
import json

# Import shared components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.config import settings
from shared.pubsub import SimplePubSub
from shared.models import NewsAlert
from news_fetcher import finnhub_fetcher
from sentiment_analyzer import sentiment_analyzer

logger = logging.getLogger(__name__)

class NewsConsumer:
    """
    Consumer that processes market events and publishes news alerts.
    
    Optimization techniques:
    1. Batch processing of similar events
    2. Intelligent filtering to reduce API calls
    3. Caching and deduplication
    4. Performance monitoring
    """
    
    def __init__(self):
        """Initialize with Redis connections and performance tracking."""
        self.pubsub = SimplePubSub(settings.redis_url)
        
        # Performance tracking
        self.processed_count = 0
        self.published_count = 0
        self.api_calls_count = 0
        self.last_processed_time = None
        
        # Optimization: Track recently processed symbols to avoid duplicates
        self.recently_processed = {}
        self.dedup_window = 1800  # 30 minutes
        
        # Quality filters - Lowered for testing
        self.min_change_percent = 3.0  # Process smaller moves for testing
        self.min_volume_threshold = 50000  # Process lower volume stocks
        
        logger.info("News consumer initialized with optimizations")
    
    def _should_process_event(self, market_event: Dict[str, Any]) -> bool:
        """
        Determine if a market event should be processed.
        
        Optimization: Filter out low-quality events to reduce API calls.
        """
        try:
            symbol = market_event.get('symbol', '')
            change_percent = market_event.get('change_percent', 0)
            volume = market_event.get('volume', 0)
            
            # Filter by change percentage
            if abs(change_percent) < self.min_change_percent:
                logger.debug(f"Skipping {symbol}: change {change_percent}% below threshold")
                return False
            
            # Filter by volume
            if volume < self.min_volume_threshold:
                logger.debug(f"Skipping {symbol}: volume {volume} below threshold")
                return False
            
            # Check if recently processed (deduplication)
            current_time = time.time()
            if symbol in self.recently_processed:
                last_processed = self.recently_processed[symbol]
                if current_time - last_processed < self.dedup_window:
                    logger.debug(f"Skipping {symbol}: recently processed")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking event processing criteria: {e}")
            return False
    
    def _process_market_event(self, market_event: Dict[str, Any]) -> None:
        """
        Process a single market event.
        
        Optimization: Comprehensive error handling and performance tracking.
        """
        start_time = time.time()
        
        try:
            symbol = market_event.get('symbol', '')
            price = market_event.get('price', 0)
            change_percent = market_event.get('change_percent', 0)
            
            logger.info(f"Processing market event: {symbol} ({change_percent:+.1f}%)")
            
            # Check if should process
            if not self._should_process_event(market_event):
                return
            
            # Fetch news from Finnhub
            logger.info(f"Fetching news for {symbol}")
            news_articles = finnhub_fetcher.get_company_news(symbol, days_back=1)
            
            if not news_articles:
                logger.warning(f"No news found for {symbol}")
                return
            
            # Analyze sentiment
            logger.info(f"Analyzing sentiment for {symbol} ({len(news_articles)} articles)")
            sentiment_result = sentiment_analyzer.analyze_news_sentiment(news_articles)
            
            # Create news alert
            news_alert = NewsAlert(
                symbol=symbol,
                price=price,
                change_percent=change_percent,
                news_sentiment=sentiment_result['sentiment_score'],
                news_count=sentiment_result['article_count'],
                news_summary=self._create_news_summary(news_articles, sentiment_result),
                top_headlines=[article.headline for article in news_articles[:3]],
                timestamp=datetime.now()
            )
            
            # Publish news alert
            success = self.pubsub.publish('news_alerts', news_alert.dict())
            
            if success:
                self.published_count += 1
                logger.info(f"Published news alert for {symbol}: sentiment={sentiment_result['sentiment_score']:.3f}")
                
                # Mark as recently processed
                self.recently_processed[symbol] = time.time()
                
                # Clean up old entries (optimization)
                self._cleanup_recent_cache()
            
            # Update performance metrics
            self.processed_count += 1
            self.last_processed_time = datetime.now().isoformat()
            
            processing_time = time.time() - start_time
            logger.info(f"Processed {symbol} in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing market event: {e}")
    
    def _create_news_summary(self, news_articles, sentiment_result) -> str:
        """
        Create a concise news summary.
        
        Optimization: Template-based summary generation for speed.
        """
        try:
            article_count = len(news_articles)
            sentiment_label = sentiment_result['sentiment_label']
            top_keywords = sentiment_result.get('top_keywords', [])
            
            if article_count == 0:
                return "No recent news available"
            
            # Create summary based on sentiment
            if sentiment_label == "positive":
                summary = f"📈 {article_count} positive news articles"
            elif sentiment_label == "negative":
                summary = f"📉 {article_count} negative news articles"
            else:
                summary = f"📊 {article_count} neutral news articles"
            
            if top_keywords:
                summary += f". Key topics: {', '.join(top_keywords[:3])}"
            
            return summary[:400]  # Limit length
            
        except Exception as e:
            logger.error(f"Error creating news summary: {e}")
            return "News summary unavailable"
    
    def _cleanup_recent_cache(self) -> None:
        """
        Clean up old entries from recently processed cache.
        
        Optimization: Prevent memory growth over time.
        """
        try:
            current_time = time.time()
            expired_symbols = [
                symbol for symbol, timestamp in self.recently_processed.items()
                if current_time - timestamp > self.dedup_window
            ]
            
            for symbol in expired_symbols:
                del self.recently_processed[symbol]
                
            if expired_symbols:
                logger.debug(f"Cleaned up {len(expired_symbols)} expired cache entries")
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    def start_listening(self) -> None:
        """
        Start listening to market events.
        
        Optimization: Robust error handling and automatic recovery.
        """
        logger.info("Starting to listen for market events...")
        
        try:
            # Subscribe to market_events channel
            self.pubsub.subscribe('market_events', self._process_market_event)
            
        except Exception as e:
            logger.error(f"Error in news consumer: {e}")
            # In a production system, we might want to retry here
            raise
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        # Get stats from dependencies
        fetcher_stats = finnhub_fetcher.get_performance_stats()
        sentiment_stats = sentiment_analyzer.get_performance_stats()
        
        return {
            "consumer_stats": {
                "processed_events": self.processed_count,
                "published_alerts": self.published_count,
                "last_processed": self.last_processed_time,
                "recently_processed_count": len(self.recently_processed)
            },
            "fetcher_stats": fetcher_stats,
            "sentiment_stats": sentiment_stats
        }

# Global instance for reuse
news_consumer = NewsConsumer()

def start_consumer():
    """
    Start the news consumer.
    
    This function is called by the Flask app in a separate thread.
    """
    try:
        logger.info("Starting news consumer...")
        news_consumer.start_listening()
        
    except Exception as e:
        logger.error(f"Failed to start news consumer: {e}")
        raise 