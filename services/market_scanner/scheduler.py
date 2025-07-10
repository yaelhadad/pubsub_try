from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import atexit

logger = logging.getLogger(__name__)

def start_scheduler():
    """
    Start the APScheduler for market scanning.
    
    Optimization: Using BackgroundScheduler to run in separate thread
    without blocking the main Flask application.
    """
    try:
        # Import scanner here to avoid circular imports
        from scanner import scanner
        
        # Create scheduler instance
        scheduler = BackgroundScheduler()
        
        # Add job to run every 5 minutes
        scheduler.add_job(
            func=scanner.scan_market,
            trigger=IntervalTrigger(minutes=5),
            id='market_scan_job',
            name='Market Scanner Job',
            replace_existing=True,
            max_instances=1  # Optimization: Prevent overlapping scans
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("Market scanner scheduler started - running every 5 minutes")
        
        # Optimization: Run initial scan immediately
        logger.info("Running initial market scan...")
        scanner.scan_market()
        
        # Ensure scheduler shuts down gracefully
        atexit.register(lambda: scheduler.shutdown())
        
        # Keep the scheduler running
        try:
            while True:
                import time
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            scheduler.shutdown()
            
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
        raise 