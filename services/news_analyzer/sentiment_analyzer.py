import logging
import time
from typing import List, Dict, Tuple
import re
from collections import Counter

# Import shared components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.models import NewsData

logger = logging.getLogger(__name__)

class OptimizedSentimentAnalyzer:
    """
    High-performance sentiment analyzer optimized for financial news.
    
    Optimization techniques:
    1. Precompiled regex patterns
    2. Cached word scoring
    3. Vectorized text processing
    4. Financial-specific vocabulary
    """
    
    def __init__(self):
        """Initialize with optimized word dictionaries and patterns."""
        
        # Financial-specific sentiment words (more accurate than general sentiment)
        self.positive_words = {
            # Strong positive (score: 2)
            'bullish', 'surge', 'soar', 'rally', 'boom', 'breakthrough', 'record', 'all-time high',
            'beat estimates', 'exceed expectations', 'strong earnings', 'profit surge',
            
            # Moderate positive (score: 1)
            'gain', 'rise', 'up', 'positive', 'growth', 'increase', 'buy', 'upgrade',
            'outperform', 'strong', 'solid', 'good', 'better', 'improved', 'optimistic',
            'confident', 'recover', 'rebound', 'momentum', 'expansion'
        }
        
        self.negative_words = {
            # Strong negative (score: -2)
            'bearish', 'crash', 'plummet', 'collapse', 'bankruptcy', 'scandal', 'fraud',
            'miss estimates', 'disappointing', 'worst', 'crisis', 'recession',
            
            # Moderate negative (score: -1)
            'loss', 'fall', 'down', 'negative', 'decline', 'decrease', 'sell', 'downgrade',
            'underperform', 'weak', 'poor', 'bad', 'worse', 'concern', 'worry',
            'risk', 'volatile', 'uncertainty', 'challenge', 'struggle'
        }
        
        # Create scoring dictionaries for optimization
        self.word_scores = {}
        for word in self.positive_words:
            if word in ['bullish', 'surge', 'soar', 'rally', 'boom', 'breakthrough', 'record']:
                self.word_scores[word] = 2
            else:
                self.word_scores[word] = 1
                
        for word in self.negative_words:
            if word in ['bearish', 'crash', 'plummet', 'collapse', 'bankruptcy', 'scandal']:
                self.word_scores[word] = -2
            else:
                self.word_scores[word] = -1
        
        # Precompile regex patterns for optimization
        self.text_cleaner = re.compile(r'[^a-zA-Z\s]')
        self.word_splitter = re.compile(r'\s+')
        
        # Performance metrics
        self.analysis_count = 0
        self.total_analysis_time = 0
        
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for analysis.
        
        Optimization: Using precompiled regex patterns.
        """
        # Remove special characters and normalize
        text = self.text_cleaner.sub(' ', text.lower())
        # Remove extra spaces
        text = self.word_splitter.sub(' ', text).strip()
        return text
    
    def _calculate_sentiment_score(self, text: str) -> Tuple[float, Dict[str, int]]:
        """
        Calculate sentiment score for text.
        
        Optimization: Fast dictionary lookups instead of complex NLP.
        """
        words = text.split()
        score = 0
        word_counts = Counter()
        
        # Process words in batches for better performance
        for word in words:
            if word in self.word_scores:
                word_score = self.word_scores[word]
                score += word_score
                word_counts[word] += 1
        
        # Normalize score based on text length (optimization)
        if len(words) > 0:
            normalized_score = score / len(words) * 10  # Scale up for better granularity
            # Clamp to -1 to 1 range
            normalized_score = max(-1, min(1, normalized_score))
        else:
            normalized_score = 0
        
        return normalized_score, dict(word_counts)
    
    def analyze_news_sentiment(self, news_articles: List[NewsData]) -> Dict[str, any]:
        """
        Analyze sentiment of multiple news articles.
        
        Optimization: Batch processing and efficient aggregation.
        """
        start_time = time.time()
        
        if not news_articles:
            return {
                "sentiment_score": 0,
                "sentiment_label": "neutral",
                "article_count": 0,
                "positive_articles": 0,
                "negative_articles": 0,
                "neutral_articles": 0,
                "top_keywords": [],
                "confidence": 0
            }
        
        total_score = 0
        article_scores = []
        all_keywords = Counter()
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        # Process articles in batch for optimization
        for article in news_articles:
            # Combine headline and summary for better analysis
            full_text = f"{article.headline} {article.summary}"
            clean_text = self._clean_text(full_text)
            
            # Calculate sentiment
            sentiment_score, keywords = self._calculate_sentiment_score(clean_text)
            
            article_scores.append(sentiment_score)
            total_score += sentiment_score
            all_keywords.update(keywords)
            
            # Categorize articles
            if sentiment_score > 0.1:
                positive_count += 1
            elif sentiment_score < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
        
        # Calculate aggregate metrics
        avg_sentiment = total_score / len(news_articles)
        
        # Determine sentiment label
        if avg_sentiment > 0.2:
            sentiment_label = "positive"
        elif avg_sentiment < -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        # Calculate confidence based on consistency
        score_variance = sum((score - avg_sentiment) ** 2 for score in article_scores) / len(article_scores)
        confidence = max(0, 1 - score_variance)  # Higher consistency = higher confidence
        
        # Get top keywords
        top_keywords = [word for word, count in all_keywords.most_common(5)]
        
        # Performance tracking
        analysis_time = time.time() - start_time
        self.analysis_count += 1
        self.total_analysis_time += analysis_time
        
        logger.info(f"Analyzed {len(news_articles)} articles in {analysis_time:.3f}s. Sentiment: {avg_sentiment:.3f}")
        
        return {
            "sentiment_score": round(avg_sentiment, 3),
            "sentiment_label": sentiment_label,
            "article_count": len(news_articles),
            "positive_articles": positive_count,
            "negative_articles": negative_count,
            "neutral_articles": neutral_count,
            "top_keywords": top_keywords,
            "confidence": round(confidence, 3)
        }
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get performance statistics for monitoring."""
        avg_time = self.total_analysis_time / max(self.analysis_count, 1)
        return {
            "analyses_performed": self.analysis_count,
            "total_analysis_time": round(self.total_analysis_time, 3),
            "average_analysis_time": round(avg_time, 3),
            "vocabulary_size": len(self.word_scores)
        }

# Global instance for reuse (optimization)
sentiment_analyzer = OptimizedSentimentAnalyzer() 