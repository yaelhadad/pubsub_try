#!/usr/bin/env python3
"""
בדיקה למניות הנסחרות ביותר (Most Actively Traded Stocks)
"""

import sys
import os
import logging
from datetime import datetime

# הוספת המודולים לpath
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'market_scanner'))

def test_most_active_stocks():
    """בדיקה למניות הנסחרות ביותר"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔍 בדיקת מניות הנסחרות ביותר מAlpha Vantage...")
    print("=" * 60)
    
    try:
        # Import scanner
        from shared.config import settings
        from services.market_scanner.scanner import scanner
        
        # בדיקת config
        print(f"✅ Redis URL: {settings.redis_url}")
        print(f"✅ Alpha Vantage API Key: {'מוגדר' if settings.alpha_vantage_api_key else 'לא מוגדר'}")
        print()
        
        # בדיקת API call
        print("📡 מבצע קריאה לAlpha Vantage API...")
        start_time = datetime.now()
        
        most_active_stocks = scanner.get_most_actively_traded()
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  זמן ביצוע: {execution_time:.2f} שניות")
        print()
        
        # בדיקת תוצאות
        if not most_active_stocks:
            print("❌ לא נמצאו מניות נסחרות!")
            return False
        
        print(f"✅ נמצאו {len(most_active_stocks)} מניות נסחרות ביותר")
        print()
        
        # הצגת Top 10
        print("📊 Top 10 מניות הנסחרות ביותר:")
        print("-" * 70)
        print(f"{'#':<3} {'סמל':<6} {'מחיר':<8} {'שינוי%':<8} {'נפח':<12} {'זמן'}")
        print("-" * 70)
        
        for i, stock in enumerate(most_active_stocks[:10]):
            print(f"{i+1:<3} {stock['symbol']:<6} ${stock['price']:<7.2f} {stock['change_percent']:+7.2f}% {stock['volume']:>11,} {stock['timestamp'][:10]}")
        
        print("-" * 70)
        
        # סטטיסטיקות
        total_volume = sum(stock['volume'] for stock in most_active_stocks)
        avg_price = sum(stock['price'] for stock in most_active_stocks) / len(most_active_stocks)
        
        print(f"📈 סטטיסטיקות:")
        print(f"   • סך הכל נפח מסחר: {total_volume:,}")
        print(f"   • מחיר ממוצע: ${avg_price:.2f}")
        print(f"   • מניה בנפח הגבוה ביותר: {most_active_stocks[0]['symbol']} ({most_active_stocks[0]['volume']:,})")
        print()
        
        # בדיקת performance
        perf_stats = scanner.get_performance_stats()
        print(f"🚀 Performance:")
        print(f"   • קריאות API: {perf_stats['api_calls_made']}")
        print(f"   • Session פעיל: {perf_stats['session_active']}")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def test_publishing():
    """בדיקה לפרסום למניות Redis"""
    
    print("\n🚀 בדיקת פרסום לRedis...")
    print("=" * 60)
    
    try:
        from shared.pubsub import SimplePubSub
        from shared.config import settings
        from shared.models import MarketEvent
        
        # יצירת PubSub connection
        pubsub = SimplePubSub(settings.redis_url)
        
        # הודעת בדיקה
        test_event = MarketEvent(
            symbol="TEST",
            price=100.0,
            change_percent=5.0,
            volume=1000000,
            timestamp=datetime.now().isoformat()
        )
        
        # פרסום
        success = pubsub.publish('market_events', test_event.dict())
        
        if success:
            print("✅ פרסום לRedis הצליח!")
            return True
        else:
            print("❌ פרסום לRedis נכשל!")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה בפרסום: {e}")
        return False

if __name__ == "__main__":
    print("🎯 בדיקת מערכת המניות הנסחרות ביותר")
    print("=" * 60)
    
    # בדיקה 1: מניות נסחרות ביותר
    stocks_test = test_most_active_stocks()
    
    # בדיקה 2: פרסום לRedis
    pubsub_test = test_publishing()
    
    # סיכום
    print("\n" + "=" * 60)
    print("🎯 סיכום בדיקות:")
    print(f"   • מניות נסחרות ביותר: {'✅ עבד' if stocks_test else '❌ נכשל'}")
    print(f"   • פרסום לRedis: {'✅ עבד' if pubsub_test else '❌ נכשל'}")
    
    if stocks_test and pubsub_test:
        print("\n🎉 כל הבדיקות עברו בהצלחה!")
        print("💡 כעת תוכל להפעיל את Market Scanner:")
        print("   python services/market_scanner/app.py")
    else:
        print("\n⚠️  יש בעיות שצריך לתקן")
        print("📝 בדוק:")
        print("   1. שמשתני הסביבה מוגדרים (.env)")
        print("   2. שRedis רץ (docker-compose up redis)")
        print("   3. שAlpha Vantage API key תקין") 