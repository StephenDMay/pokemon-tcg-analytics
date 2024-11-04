from pydantic_settings import BaseSettings
from pydantic import field_validator, SecretStr, PostgresDsn
from typing import Optional, List, Union
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Pokemon TCG Analytics"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Pokemon TCG Analytics and Deck Building Assistant"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Database Settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: SecretStr = SecretStr(os.getenv("POSTGRES_PASSWORD", ""))
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "pokemon_tcg")
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # API Keys
    POKEMON_TCG_API_KEY: SecretStr = SecretStr(os.getenv("POKEMON_TCG_API_KEY", ""))
    LIMITLESS_API_KEY: Optional[SecretStr] = SecretStr(os.getenv("LIMITLESS_API_KEY", ""))  # Added this line
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @field_validator("POSTGRES_USER")
    def validate_postgres_user(cls, v: str) -> str:
        if not v:
            raise ValueError("POSTGRES_USER must be set in environment")
        return v
    
    @field_validator("POSTGRES_PASSWORD")
    def validate_postgres_password(cls, v: SecretStr) -> SecretStr:
        if not v.get_secret_value():
            raise ValueError("POSTGRES_PASSWORD must be set in environment")
        return v
    
    @field_validator("DATABASE_URL", mode='before')
    def assemble_db_url(cls, v: Optional[str], info) -> Optional[str]:
        if v:
            return v

        # Access the data from the validation context
        data = info.data
        
        # Get the password and handle SecretStr
        password = data.get("POSTGRES_PASSWORD")
        if isinstance(password, SecretStr):
            password = password.get_secret_value()
            
        # Construct the URL string manually
        return f"postgresql://{data.get('POSTGRES_USER')}:{password}@{data.get('POSTGRES_SERVER')}:{data.get('POSTGRES_PORT')}/{data.get('POSTGRES_DB')}"
    
    @field_validator("POKEMON_TCG_API_KEY")
    def validate_pokemon_api_key(cls, v: SecretStr) -> SecretStr:
        if not v.get_secret_value():
            raise ValueError("POKEMON_TCG_API_KEY must be set in environment")
        return v
    
    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v.upper()
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        # Allow extra fields in the environment
        extra = "ignore"

# Create settings instance
settings = Settings()

# Validate the settings on import
def validate_settings() -> None:
    """Validate critical settings on startup"""
    required_settings = [
        ("POSTGRES_USER", settings.POSTGRES_USER),
        ("POSTGRES_PASSWORD", settings.POSTGRES_PASSWORD.get_secret_value()),
        ("POKEMON_TCG_API_KEY", settings.POKEMON_TCG_API_KEY.get_secret_value()),
    ]
    
    missing_settings = [
        name for name, value in required_settings
        if not value
    ]
    
    if missing_settings:
        raise ValueError(
            "Missing required environment variables: "
            f"{', '.join(missing_settings)}"
        )

# Validate settings when the module is loaded
validate_settings()