"""
Configuration robuste avec v    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Cache (mémoire gratuit)
    cache_ttl: int = 3600  # 1 houron Pydantic
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Redshift Configuration
    redshift_user: str
    redshift_password: str
    redshift_host: str
    redshift_port: int = 5439
    redshift_db: str
    redshift_schema: str = "public"
    
    # API Keys
    google_api_key: str
    
    # Application Settings
    app_name: str = "TextToSQL API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database Pool Settings
    db_pool_size: int = 10
    db_pool_overflow: int = 20
    db_pool_timeout: int = 30
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour
    
    # Caching
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    @field_validator('redshift_port')
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()
    
    @property
    def redshift_dsn(self) -> str:
        return f"redshift+psycopg2://{self.redshift_user}:{self.redshift_password}@{self.redshift_host}:{self.redshift_port}/{self.redshift_db}"
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore les champs supplémentaires
    }

# Instance globale des settings
settings = Settings()
