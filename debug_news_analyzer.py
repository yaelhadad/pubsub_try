#!/usr/bin/env python3
"""
אבחון ספציפי לNews Analyzer
"""

import sys
import os
import threading
import time
import json
from datetime import datetime

# הוספת הpath של המודולים
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'news_analyzer'))

def test_imports():
    """בדיקת יבואים"""
    print("🔍 בודק יבואים...")
    
    try:
        from shared.config import settings
        print("✅ shared.config - OK")
        
        from shared.pubsub import SimplePubSub
        print("✅ shared.pubsub - OK")
        
        from shared.models import MarketEvent
        print("✅ shared.models - OK")
        
        from services.news_analyzer.news_fetcher import FinnhubNewsFetcher
        print("✅ news_fetcher - OK")
        
        from services.news_analyzer.consumer import NewsConsumer
        print("✅ consumer - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ יבוא נכשל: {e}")
        return False

def test_consumer_creation():
    """בדיקת יצירת NewsConsumer"""
    print("\n🔍 בודק יצירת NewsConsumer...")
    
    try:
        from shared.config import settings
        from services.news_analyzer.consumer import NewsConsumer
        
        consumer = NewsConsumer(settings.redis_url)
        print("✅ NewsConsumer נוצר בהצלחה")
        
        # בדיקת שהוא מוכן
        print(f"✅ Redis URL: {settings.redis_url}")
        print(f"✅ Finnhub Key: {'קיים' if settings.finnhub_api_key else 'חסר'}")
        
        return consumer
        
    except Exception as e:
        print(f"❌ יצירת NewsConsumer נכשלה: {e}")
        print(f"   פרטי שגיאה: {str(e)}")
        return None

def test_consumer_manual(consumer):
    """בדיקת עיבוד הודעה ידנית"""
    print("\n🔍 בודק עיבוד הודעה ידנית...")
    
    try:
        # הודעת בדיקה
        test_message = {
            "symbol": "AAPL",
            "price": 150.0,
            "change_percent": 8.0,
            "volume": 500000,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📨 שולח הודעת בדיקה: {test_message}")
        
        # עיבוד ידני
        consumer.process_message(test_message)
        print("✅ עיבוד הודעה הושלם")
        
        return True
        
    except Exception as e:
        print(f"❌ עיבוד הודעה נכשל: {e}")
        print(f"   פרטי שגיאה: {str(e)}")
        return False

def test_consumer_thread():
    """בדיקת consumer thread"""
    print("\n🔍 בודק consumer thread...")
    
    try:
        from shared.config import settings
        from services.news_analyzer.consumer import NewsConsumer
        
        consumer = NewsConsumer(settings.redis_url)
        
        # יצירת thread
        def run_consumer():
            print("📡 מתחיל consumer thread...")
            consumer.start_consuming()
        
        thread = threading.Thread(target=run_consumer)
        thread.daemon = True
        thread.start()
        
        print("✅ Consumer thread התחיל")
        
        # מחכה קצת
        time.sleep(2)
        
        if thread.is_alive():
            print("✅ Consumer thread רץ")
            return True
        else:
            print("❌ Consumer thread נעצר")
            return False
            
    except Exception as e:
        print(f"❌ Consumer thread נכשל: {e}")
        return False

def test_full_flow():
    """בדיקת זרימה מלאה"""
    print("\n🔍 בודק זרימה מלאה...")
    
    try:
        from shared.config import settings
        from shared.pubsub import SimplePubSub
        from services.news_analyzer.consumer import NewsConsumer
        
        # יצירת publisher
        publisher = SimplePubSub(settings.redis_url)
        
        # יצירת consumer
        consumer = NewsConsumer(settings.redis_url)
        
        # הפעלת consumer בthread
        def run_consumer():
            consumer.start_consuming()
        
        thread = threading.Thread(target=run_consumer)
        thread.daemon = True
        thread.start()
        
        # מחכה שהthread יתחיל
        time.sleep(2)
        
        # שליחת הודעה
        test_message = {
            "symbol": "AAPL",
            "price": 150.0,
            "change_percent": 8.0,
            "volume": 500000,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📨 שולח market event: {test_message}")
        result = publisher.publish('market_events', test_message)
        print(f"✅ פרסום הצליח: {result}")
        
        # מחכה לעיבוד
        print("⏰ מחכה 5 שניות לעיבוד...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ זרימה מלאה נכשלה: {e}")
        return False

def main():
    print("🔧 אבחון News Analyzer")
    print("=" * 50)
    
    # בדיקות
    imports_ok = test_imports()
    if not imports_ok:
        print("❌ יבואים נכשלו - עוצר כאן")
        return
    
    consumer = test_consumer_creation()
    if not consumer:
        print("❌ יצירת consumer נכשלה - עוצר כאן")
        return
    
    manual_ok = test_consumer_manual(consumer)
    thread_ok = test_consumer_thread()
    flow_ok = test_full_flow()
    
    print("\n" + "=" * 50)
    print("🎯 תוצאות:")
    print(f"✅ Imports: {'✓' if imports_ok else '✗'}")
    print(f"✅ Consumer Creation: {'✓' if consumer else '✗'}")
    print(f"✅ Manual Processing: {'✓' if manual_ok else '✗'}")
    print(f"✅ Thread: {'✓' if thread_ok else '✗'}")
    print(f"✅ Full Flow: {'✓' if flow_ok else '✗'}")
    
    if all([imports_ok, consumer, manual_ok, thread_ok]):
        print("\n🎉 News Analyzer עובד תקין!")
        print("💡 אם עדיין לא רואה פלט, בדוק שMarket Scanner מפרסם events")
    else:
        print("\n⚠️  יש בעיות ב-News Analyzer")
        
    print("\n📝 עזרה:")
    print("1. הפעל Redis: docker-compose up redis")
    print("2. הפעל Market Scanner: python services/market_scanner/app.py")
    print("3. הפעל News Analyzer: python services/news_analyzer/app.py")
    print("4. הפעל בדיקה: python debug_news_analyzer.py")

if __name__ == "__main__":
    main() 