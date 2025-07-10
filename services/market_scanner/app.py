from flask import Flask, jsonify
import logging
import threading
from scheduler import start_scheduler

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({"status": "healthy", "service": "market_scanner"})

@app.route('/status')
def status():
    """Status endpoint showing service information."""
    return jsonify({
        "service": "market_scanner",
        "version": "1.0.0",
        "status": "running",
        "features": ["alpha_vantage_integration", "redis_pubsub", "scheduled_scanning"]
    })

def initialize_scheduler():
    """Initialize the scheduler in a separate thread for optimization."""
    try:
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Market scanner scheduler initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {e}")

if __name__ == '__main__':
    # Initialize scheduler before starting Flask app
    initialize_scheduler()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 