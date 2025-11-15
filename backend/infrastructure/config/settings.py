"""
Application Settings & Configuration

Centralized configuration management using Pydantic Settings.
Loads from environment variables with .env file support.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List



import os
_env_file = os.environ.get("ENV_FILE", ".env")

class Settings(BaseSettings):
    """Main application settings"""
    model_config = SettingsConfigDict(
        env_file=_env_file, env_file_encoding="utf-8", case_sensitive=False
    )

    # Application
    app_name: str = "AurumAI Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # Database (PostgreSQL)
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "testuser"
    db_password: str = "testpass"
    db_name: str = "testdb"
    db_echo: bool = False

    # TimescaleDB
    tsdb_host: str = "localhost"
    tsdb_port: int = 5432
    tsdb_user: str = "testuser"
    tsdb_password: str = "testpass"
    tsdb_name: str = "testdb"

    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str = "testuser"
    mqtt_password: str = "testpass"
    mqtt_topic_prefix: str = "aurumai"

    # Security
    secret_key: str = "testsecret"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # Multi-tenant
    default_region: str = "EU"
    enable_multi_region: bool = True

    # ESG
    esg_default_factor_source: str = "IPCC_2019"
    esg_calculation_method: str = "direct"

    # ML Models
    ml_models_path: str = "./models"
    ml_inference_enabled: bool = True
    ml_model_version: str = "v1.0.0"

    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True

    # Feature Flags
    feature_predictive: bool = True
    feature_carbon: bool = True
    feature_energy: bool = True
    feature_water: bool = False
    feature_analytics: bool = True

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def async_database_url(self) -> str:
        """Construct async PostgreSQL database URL"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def tsdb_url(self) -> str:
        """Construct TimescaleDB URL"""
        return f"postgresql://{self.tsdb_user}:{self.tsdb_password}@{self.tsdb_host}:{self.tsdb_port}/{self.tsdb_name}"

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() == "development"



# Global settings instance
try:
    settings = Settings()
except Exception as e:
    import sys
    from pydantic import ValidationError
    print(f"Error cargando configuración: {e}", file=sys.stderr)
    if isinstance(e, ValidationError):
        print("Variables faltantes o inválidas:", file=sys.stderr)
        for err in e.errors():
            loc = '.'.join(str(x) for x in err['loc'])
            msg = err['msg']
            print(f"- {loc}: {msg}", file=sys.stderr)
    settings = None

# Ejemplo de variables obligatorias para .env:
# db_host=localhost
# db_user=testuser
# db_password=testpass
# db_name=testdb
# tsdb_host=localhost
# tsdb_user=testuser
# tsdb_password=testpass
# tsdb_name=testdb
# mqtt_broker_host=localhost
# mqtt_username=testuser
# mqtt_password=testpass
# secret_key=testsecret
