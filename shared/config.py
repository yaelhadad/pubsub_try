# shared/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional

class Settings(BaseSettings):
    """
    Settings with intelligent environment variable loading.
    Looks for .env file in multiple locations with fallbacks.
    """
    redis_url: str = "redis://localhost:6379"
    
    # Alpha Vantage API - using demo key as fallback for testing
    alpha_vantage_api_key: str = Field(
        default="demo", 
        env="ALPHA_VANTAGE_API_KEY",
        description="Alpha Vantage API key (demo key works for testing)"
    )
    
    # News APIs - optional for basic functionality
    news_api_key: Optional[str] = Field(
        default=None, 
        env="NEWS_API_KEY",
        description="News API key (optional)"
    )
    
    finnhub_api_key: Optional[str] = Field(
        default=None, 
        env="FINNHUB_API_KEY",
        description="Finnhub API key (optional)"
    )
    
    # Email configuration - optional for notifications
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    class Config:
        # Try multiple .env file locations
        env_file_encoding = 'utf-8'
        case_sensitive = False
        
    def __init__(self, **kwargs):
        # Try to find .env file in multiple locations
        possible_env_files = [
            os.path.join(os.path.dirname(__file__), ".env"),  # shared/.env
            os.path.join(os.path.dirname(__file__), "..", ".env"),  # root/.env
            ".env",  # current directory
        ]
        
        env_file_found = None
        for env_file in possible_env_files:
            if os.path.exists(env_file):
                env_file_found = env_file
                break
        
        if env_file_found:
            print(f"✅ Loading environment from: {env_file_found}")
            super().__init__(_env_file=env_file_found, **kwargs)
        else:
            print("⚠️  No .env file found, using environment variables and defaults")
            super().__init__(**kwargs)

# Create settings instance
settings = Settings()

# Print configuration status
def print_config_status():
    """Print current configuration status for debugging."""
    print("🔧 Configuration Status:")
    print(f"   Redis URL: {settings.redis_url}")
    print(f"   Alpha Vantage API: {'✅ Set' if settings.alpha_vantage_api_key else '❌ Missing'}")
    print(f"   News API: {'✅ Set' if settings.news_api_key else '⚠️  Optional'}")
    print(f"   Finnhub API: {'✅ Set' if settings.finnhub_api_key else '⚠️  Optional'}")
    print(f"   Email Config: {'✅ Set' if settings.smtp_username else '⚠️  Optional'}")

if __name__ == "__main__":
    print_config_status()