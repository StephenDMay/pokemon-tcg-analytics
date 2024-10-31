# Similar to appsettings.json and IConfiguration in ASP.NET Core
# Manages application settings and environment variables
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Like configuration sections in appsettings.json
    PROJECT_NAME: str = "Pokemon TCG Analytics"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Pokemon TCG Analytics and Deck Building Tool"
    POKEMON_TCG_API_KEY: str = ""
    LIMITLESS_API_KEY: Optional[str] = None
    
    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    class Config:
        # Like user secrets in .NET
        env_file = ".env"
        extra = "ignore"

settings = Settings()