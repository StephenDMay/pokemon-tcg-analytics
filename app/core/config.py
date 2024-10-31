# Similar to appsettings.json and IConfiguration in ASP.NET Core
# Manages application settings and environment variables
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Like configuration sections in appsettings.json
    PROJECT_NAME: str = "Pokemon TCG Analytics"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for Pokemon TCG card analysis and deck building"
    POKEMON_TCG_API_KEY: str = ""
    
    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    class Config:
        # Like user secrets in .NET
        env_file = ".env"

settings = Settings()