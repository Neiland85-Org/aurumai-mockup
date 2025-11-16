"""
Application Settings & Configuration

Centralized configuration management using Pydantic Settings.
Loads from environment variables with .env file support.

SECURITY NOTICE:
- All sensitive variables (passwords, secret keys) are REQUIRED
- No default values for production secrets
- Development defaults only for non-sensitive settings
"""

import os
from typing import Any, List

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_file = os.environ.get("ENV_FILE", ".env")


class Settings(BaseSettings):
    """Main application settings

    Critical variables (SECRET_KEY, DB_PASSWORD) have NO defaults
    and will raise ValidationError if not provided in environment.
    """

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
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
    # CRITICAL: DB_PASSWORD is REQUIRED (no default)
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "aurumai"
    db_password: str = Field(..., description="Database password (REQUIRED)")
    db_name: str = "aurumai"
    db_echo: bool = False

    # TimescaleDB
    # CRITICAL: TSDB_PASSWORD is REQUIRED (no default)
    tsdb_host: str = "localhost"
    tsdb_port: int = 5432
    tsdb_user: str = "aurumai"
    tsdb_password: str = Field(..., description="TimescaleDB password (REQUIRED)")
    tsdb_name: str = "aurumai_timeseries"

    # MQTT
    # CRITICAL: MQTT_PASSWORD is REQUIRED (no default)
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: str = "aurumai"
    mqtt_password: str = Field(..., description="MQTT password (REQUIRED)")
    mqtt_topic_prefix: str = "aurumai"

    # Security
    # CRITICAL: SECRET_KEY is REQUIRED (no default)
    secret_key: str = Field(
        ..., min_length=32, description="Secret key for JWT/sessions (REQUIRED, min 32 chars)"
    )
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

    # Observability - Logging
    log_format: str = "json"  # json or text
    log_to_file: bool = False
    log_file_path: str = "./logs/aurumai.log"

    # Observability - Tracing
    tracing_enabled: bool = False
    tracing_service_name: str = "aurumai-backend"
    tracing_otlp_endpoint: str = ""  # e.g., "http://localhost:4317"
    tracing_console_export: bool = False  # Export to console for debugging

    # Resilience - Retry Policy
    retry_max_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    retry_multiplier: float = 2.0

    # Resilience - Circuit Breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_fail_max: int = 5
    circuit_breaker_timeout: float = 60.0  # seconds

    # Resilience - Timeouts
    timeout_connect: float = 5.0  # Connection timeout in seconds
    timeout_read: float = 30.0  # Read timeout in seconds
    timeout_write: float = 30.0  # Write timeout in seconds
    timeout_pool: float = 5.0  # Pool timeout in seconds
    timeout_db: float = 30.0  # Database timeout in seconds

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Comma-separated list of allowed CORS origins",
    )
    cors_allow_credentials: bool = True

    # Feature Flags
    feature_predictive: bool = True
    feature_carbon: bool = True
    feature_energy: bool = True
    feature_water: bool = False
    feature_analytics: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from comma-separated string or JSON array"""
        if isinstance(v, str):
            # If it's a comma-separated string, split it
            if "," in v:
                return [origin.strip() for origin in v.split(",")]
            # If it's a JSON array string, parse it
            elif v.startswith("["):
                import json

                return json.loads(v)
            # Single origin
            return [v]
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate SECRET_KEY is strong enough for production"""
        if info.data.get("environment", "").lower() == "production":
            if len(v) < 64:
                raise ValueError(
                    "SECRET_KEY must be at least 64 characters in production. "
                    "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(64))'"
                )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("debug")
    @classmethod
    def validate_debug_in_production(cls, v: bool, info: ValidationInfo) -> bool:
        """Ensure DEBUG is False in production"""
        if info.data.get("environment", "").lower() == "production" and v:
            raise ValueError("DEBUG must be False in production environment")
        return v

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
settings: Settings
try:
    # type: ignore[call-arg] - BaseSettings loads from environment, not constructor args
    settings = Settings()  # type: ignore[call-arg]
except Exception as e:  # pragma: no cover - configuration errors must surface early
    import sys

    from pydantic import ValidationError

    print(f"Error cargando configuración: {e}", file=sys.stderr)
    if isinstance(e, ValidationError):
        print("Variables faltantes o inválidas:", file=sys.stderr)
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            msg = err["msg"]
            print(f"- {loc}: {msg}", file=sys.stderr)
    print(
        "\n💡 Asegúrate de que el archivo .env existe y contiene todas las variables requeridas",
        file=sys.stderr,
    )
    sys.exit(1)
