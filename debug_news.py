#!/usr/bin/env python3
"""
סקריפט אבחון לבדיקת News Analyzer
"""

import sys
import os
import requests
import redis
import json
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
from shared.config import settings

def check_services():
    """בדוק שכל השירותים רצים"""
    print("🔍 בודק שירותים...")
    
    # Market Scanner
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Market Scanner רץ")
        else:
            print(f"❌ Market Scanner לא תקין: {response.status_code}")
    except:
        print("❌ Market Scanner לא רץ")
    
    # News Analyzer
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        if response.status_code == 200:
            print("✅ News Analyzer רץ")
        else:
            print(f"❌ News Analyzer לא תקין: {response.status_code}")
    except:
        print("❌ News Analyzer לא רץ")

def check_redis():
    """בדוק Redis connection"""
    print("\n🔍 בודק Redis...")
    
    try:
        r = redis.Redis.from_url(settings.redis_url)
        r.ping()
        print("✅ Redis connection עובד")
        
        # בדוק messages שנשלחו
        pubsub = r.pubsub()
        pubsub.psubscribe("*")
        print("📡 מאזין להודעות ב-Redis (לחץ Ctrl+C להפסיק)...")
        
        # האזן ל-5 שניות
        import time
        start_time = time.time()
        while time.time() - start_time < 5:
            message = pubsub.get_message(timeout=1)
            if message and message['type'] == 'pmessage':
                channel = message['channel']
                data = message['data']
                print(f"📨 הודעה בערוץ {channel}: {data[:100]}...")
        
        print("⏰ סיימתי להאזין")
        
    except Exception as e:
        print(f"❌ Redis connection נכשל: {e}")

def check_finnhub_api():
    """בדוק Finnhub API"""
    print("\n🔍 בודק Finnhub API...")
    
    if not settings.finnhub_api_key:
        print("❌ FINNHUB_API_KEY לא מוגדר")
        return
    
    try:
        url = "https://finnhub.io/api/v1/company-news"
        headers = {'X-Finnhub-Token': settings.finnhub_api_key}
        params = {
            'symbol': 'AAPL',
            'from': '2025-01-14',
            'to': '2025-01-15'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            news_data = response.json()
            print(f"✅ Finnhub API עובד - {len(news_data)} חדשות עבור AAPL")
        elif response.status_code == 401:
            print("❌ Finnhub API key לא תקין")
        else:
            print(f"❌ Finnhub API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Finnhub API נכשל: {e}")

def send_test_event():
    """שלח market event לבדיקה"""
    print("\n🧪 שולח market event לבדיקה...")
    
    try:
        r = redis.Redis.from_url(settings.redis_url)
        
        test_event = {
            "symbol": "TSLA",
            "price": 250.0,
            "change_percent": 8.5,
            "volume": 2000000,
            "timestamp": datetime.now().isoformat()
        }
        
        result = r.publish('market_events', json.dumps(test_event))
        
        if result > 0:
            print(f"✅ שלחתי market event ל-{result} subscribers")
            print("👀 בדוק בלוגים של News Analyzer אם הוא מעבד את ההודעה")
        else:
            print("⚠️  שלחתי market event אבל אין subscribers")
            
    except Exception as e:
        print(f"❌ שליחת market event נכשלה: {e}")

def check_metrics():
    """בדוק metrics של השירותים"""
    print("\n📊 בודק metrics...")
    
    try:
        response = requests.get("http://localhost:5001/metrics", timeout=5)
        if response.status_code == 200:
            metrics = response.json()
            print("📈 News Analyzer metrics:")
            print(f"   Events processed: {metrics.get('processed_events', 0)}")
            print(f"   Alerts published: {metrics.get('published_alerts', 0)}")
            print(f"   API calls made: {metrics.get('api_calls_made', 0)}")
        else:
            print("❌ לא הצלחתי לקבל metrics")
    except:
        print("❌ News Analyzer לא זמין למetrics")

if __name__ == "__main__":
    print("🔧 אבחון מערכת News Analyzer")
    print("=" * 40)
    
    check_services()
    check_redis()
    check_finnhub_api()
    send_test_event()
    check_metrics()
    
    print("\n" + "=" * 40)
    print("🎯 סיכום:")
    print("1. אם כל הבדיקות עברו - המערכת תקינה")
    print("2. אם יש בעיות - עקוב אחר ההודעות לעיל")
    print("3. הפעל: python debug_news.py")
    print("4. אחרי הבדיקה - צפה בלוגים של News Analyzer") 