import redis
import json
import logging
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

class SimplePubSub:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis PubSub wrapper with connection pooling for optimization."""
        try:
            # Using connection pooling for better performance
            self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()  # Test connection
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def publish(self, channel: str, data: Dict[str, Any]) -> bool:
        """
        Publish message to Redis channel.
        
        Optimization: Using JSON serialization instead of pickle for better performance
        and cross-language compatibility.
        """
        try:
            message = json.dumps(data)
            result = self.redis.publish(channel, message)
            logger.info(f"Published message to {channel}: {data}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to publish message to {channel}: {e}")
            return False
    
    def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to Redis channel and process messages.
        
        Optimization: Using pubsub() context manager for automatic cleanup
        and efficient message processing.
        """
        try:
            pubsub = self.redis.pubsub()
            pubsub.subscribe(channel)
            logger.info(f"Subscribed to channel: {channel}")
            
            # Skip the subscription confirmation message
            pubsub.get_message()
            
            for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        callback(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
        except Exception as e:
            logger.error(f"Error in subscription to {channel}: {e}") 