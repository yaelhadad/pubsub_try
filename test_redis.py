#!/usr/bin/env python3
"""
בדיקת Redis connection ו-PubSub
"""

import sys
import os
import redis
import json
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
from shared.config import settings

def test_redis_basic():
    """בדיקת Redis connection בסיסי"""
    print("🔍 בודק Redis connection...")
    
    try:
        r = redis.Redis.from_url(settings.redis_url)
        result = r.ping()
        print(f"✅ Redis ping: {result}")
        return r
    except Exception as e:
        print(f"❌ Redis connection נכשל: {e}")
        return None

def test_pubsub_publish(r):
    """בדיקת פרסום הודעות"""
    print("\n🔍 בודק פרסום הודעות...")
    
    try:
        # פרסום הודעת בדיקה
        test_message = {
            "symbol": "TEST",
            "price": 100.0,
            "change_percent": 8.0,
            "volume": 500000,
            "timestamp": datetime.now().isoformat()
        }
        
        result = r.publish('market_events', json.dumps(test_message))
        print(f"✅ פרסמתי market_events ל-{result} subscribers")
        
        if result == 0:
            print("⚠️  אין subscribers ל-market_events")
        
        return result > 0
        
    except Exception as e:
        print(f"❌ פרסום נכשל: {e}")
        return False

def test_pubsub_subscribe(r):
    """בדיקת האזנה להודעות"""
    print("\n🔍 בודק האזנה להודעות...")
    
    try:
        pubsub = r.pubsub()
        pubsub.subscribe('market_events')
        
        print("📡 מאזין ל-market_events...")
        print("📝 שלח market event בטרמינל אחר:")
        print('redis-cli PUBLISH market_events \'{"symbol":"TEST","price":100}\'')
        print("⏰ מחכה 10 שניות להודעות...")
        
        # מחכה להודעות
        start_time = time.time()
        while time.time() - start_time < 10:
            message = pubsub.get_message(timeout=1)
            if message:
                if message['type'] == 'subscribe':
                    print(f"✅ הירשמתי לערוץ {message['channel']}")
                elif message['type'] == 'message':
                    print(f"📨 קיבלתי הודעה: {message['data']}")
                    return True
        
        print("⚠️  לא קיבלתי הודעות תוך 10 שניות")
        return False
        
    except Exception as e:
        print(f"❌ האזנה נכשלה: {e}")
        return False

def test_news_analyzer_connection():
    """בדיקה ספציפית לNews Analyzer"""
    print("\n🔍 בודק News Analyzer connection...")
    
    try:
        # ייבוא מודולים של News Analyzer
        sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'news_analyzer'))
        
        from shared.pubsub import SimplePubSub
        
        # יצירת connection כמו בNews Analyzer
        pubsub = SimplePubSub(settings.redis_url)
        print("✅ SimplePubSub נוצר בהצלחה")
        
        # בדיקת publish
        test_data = {"test": "message"}
        result = pubsub.publish('test_channel', test_data)
        print(f"✅ SimplePubSub publish: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ News Analyzer connection נכשל: {e}")
        print(f"   פרטי שגיאה: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 בדיקת Redis ו-PubSub")
    print("=" * 40)
    
    # בדיקות
    r = test_redis_basic()
    if not r:
        print("❌ Redis לא זמין - עצור כאן")
        exit(1)
    
    pub_result = test_pubsub_publish(r)
    sub_result = test_pubsub_subscribe(r)
    news_result = test_news_analyzer_connection()
    
    print("\n" + "=" * 40)
    print("🎯 תוצאות:")
    print(f"✅ Redis connection: {'✓' if r else '✗'}")
    print(f"✅ Publish: {'✓' if pub_result else '✗'}")
    print(f"✅ Subscribe: {'✓' if sub_result else '✗'}")
    print(f"✅ News Analyzer: {'✓' if news_result else '✗'}")
    
    if all([r, pub_result, news_result]):
        print("\n🎉 Redis ו-PubSub עובדים תקין!")
        print("💡 אם News Analyzer עדיין לא מאזין, הבעיה בקוד Python")
    else:
        print("\n⚠️  יש בעיות שצריך לתקן")
        
    print("\n📝 עזרה:")
    print("1. וודא שRedis רץ: docker-compose up redis")
    print("2. וודא שNews Analyzer רץ: python services/news_analyzer/app.py")
    print("3. הפעל: python test_redis.py") 