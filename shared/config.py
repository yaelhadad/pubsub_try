import os
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    alpha_vantage_key: str = os.getenv("ALPHA_VANTAGE_KEY")
    news_api_key: str = os.getenv("NEWS_API_KEY")
    
    # Email settings
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME")
    smtp_password: str = os.getenv("SMTP_PASSWORD")
    
    class Config:
        env_file = ".env"

settings = Settings() 