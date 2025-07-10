from flask import Flask, jsonify
import logging
import threading
from consumer import start_consumer

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "healthy", "service": "news_analyzer"})

@app.route('/status')
def status():
    """Status endpoint showing service information."""
    return jsonify({
        "service": "news_analyzer",
        "version": "1.0.0",
        "status": "running",
        "features": ["finnhub_integration", "sentiment_analysis", "redis_pubsub"]
    })

@app.route('/metrics')
def metrics():
    """Metrics endpoint for monitoring performance."""
    try:
        from consumer import news_consumer
        return jsonify({
            "processed_events": getattr(news_consumer, 'processed_count', 0),
            "published_alerts": getattr(news_consumer, 'published_count', 0),
            "api_calls_made": getattr(news_consumer, 'api_calls_count', 0),
            "last_processed": getattr(news_consumer, 'last_processed_time', None)
        })
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return jsonify({"error": "Metrics unavailable"}), 500

def initialize_consumer():
    """Initialize the news consumer in a separate thread for optimization."""
    try:
        # Using daemon thread to ensure clean shutdown
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()
        logger.info("News analyzer consumer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize consumer: {e}")

if __name__ == '__main__':
    # Initialize consumer before starting Flask app
    initialize_consumer()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5001, debug=True) 