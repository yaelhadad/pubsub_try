from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class StockAlert(BaseModel):
    """Model for stock market events with validation."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    price: float = Field(..., gt=0, description="Current stock price")
    change_percent: float = Field(..., description="Percentage change")
    volume: int = Field(..., ge=0, description="Trading volume")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")

class NewsAlert(BaseModel):
    """Model for news-based alerts with sentiment analysis."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    price: float = Field(..., gt=0, description="Current stock price")
    change_percent: float = Field(..., description="Percentage change")
    news_sentiment: float = Field(..., ge=0, le=1, description="Sentiment score (0-1)")
    news_summary: str = Field(..., max_length=500, description="Brief news summary")
    timestamp: datetime = Field(default_factory=datetime.now, description="Alert timestamp")

class MarketEvent(BaseModel):
    """Model for market scanner events - optimized for fast serialization."""
    symbol: str
    price: float
    change_percent: float
    volume: int
    timestamp: str  # Using string for faster JSON serialization
    
    class Config:
        # Optimization: Enable JSON encoders for better performance
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 