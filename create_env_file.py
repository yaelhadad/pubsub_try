#!/usr/bin/env python3
"""
סקריפט עזר ליצירת קובץ .env עם משתני הסביבה הנדרשים
"""

import os

def create_env_file():
    """יצירת קובץ .env עם ערכי ברירת מחדל"""
    
    env_content = """# Stock Alert System Environment Variables
# =====================================

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Alpha Vantage API (for stock data)
# Get your free API key from: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=demo

# News API Configuration (Optional)
# Get your free API key from: https://newsapi.org/
# NEWS_API_KEY=your_news_api_key_here

# Finnhub API (for financial news) (Optional)
# Get your free API key from: https://finnhub.io/
# FINNHUB_API_KEY=your_finnhub_api_key_here

# Email Configuration (Optional - for notifications)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your_email@gmail.com
# SMTP_PASSWORD=your_app_password

# Note: 
# - The 'demo' key for Alpha Vantage works for testing but has limitations
# - Uncomment and fill in the optional keys as needed
# - Keep this file secure and never commit it to git
"""

    # קביעת מיקום הקובץ
    env_file_path = ".env"
    
    try:
        # בדיקה אם הקובץ כבר קיים
        if os.path.exists(env_file_path):
            response = input(f"⚠️  הקובץ {env_file_path} כבר קיים. האם להחליף אותו? (y/N): ")
            if response.lower() not in ['y', 'yes', 'כן']:
                print("❌ ביטול יצירת הקובץ")
                return False
        
        # יצירת הקובץ
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ הקובץ {env_file_path} נוצר בהצלחה!")
        print("\n📝 הוראות:")
        print("1. ערוך את הקובץ .env עם המפתחות שלך")
        print("2. קבל מפתח Alpha Vantage חינם מ: https://www.alphavantage.co/support/#api-key")
        print("3. הקובץ .env לא יישמר בגיט (בטוח)")
        print("\n🧪 לבדיקה מהירה:")
        print("   python shared/config.py")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה ביצירת הקובץ: {e}")
        return False

def test_config():
    """בדיקת הconfig הנוכחי"""
    print("🔍 בדיקת Config נוכחי...")
    try:
        import sys
        sys.path.append('shared')
        from config import print_config_status
        print_config_status()
        return True
    except Exception as e:
        print(f"❌ שגיאה בבדיקת Config: {e}")
        return False

if __name__ == "__main__":
    print("🛠️  סקריפט יצירת קובץ .env")
    print("=" * 40)
    
    # יצירת קובץ .env
    if create_env_file():
        print("\n" + "=" * 40)
        test_config()
    
    print("\n💡 לאחר עריכת .env, הפעל:")
    print("   python test_most_active.py") 