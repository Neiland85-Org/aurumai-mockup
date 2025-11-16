#!/usr/bin/env python3
"""
Secret Key Generator for AurumAI Platform
Generates cryptographically secure keys for different environments.

Usage:
    python tools/generate_secrets.py
    python tools/generate_secrets.py --length 64
"""

import argparse
import secrets
import string
from pathlib import Path


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key.
    
    Args:
        length: Length of the key (default 32 characters)
        
    Returns:
        URL-safe base64 encoded string
    """
    return secrets.token_urlsafe(length)


def generate_password(length: int = 16) -> str:
    """
    Generate a strong password with mixed characters.
    
    Args:
        length: Length of the password (default 16 characters)
        
    Returns:
        Strong password with uppercase, lowercase, digits, and symbols
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def create_env_template(env_type: str = "development") -> str:
    """
    Create .env template with generated secrets.
    
    Args:
        env_type: Environment type (development, staging, production)
        
    Returns:
        .env file content as string
    """
    secret_key = generate_secret_key(32)
    db_password = generate_password(20)
    mqtt_password = generate_password(16)
    
    template = f"""# AurumAI Platform - {env_type.upper()} Environment
# Generated on: {Path(__file__).stat().st_mtime}
# WARNING: Keep this file secret! Never commit to git!

# ============================================
# Application Settings
# ============================================
ENVIRONMENT={env_type}
APP_NAME=AurumAI Platform
APP_VERSION=0.1.0
LOG_LEVEL={"DEBUG" if env_type == "development" else "INFO"}

# ============================================
# Security Settings
# ============================================
SECRET_KEY={secret_key}

# ============================================
# Database Configuration (PostgreSQL)
# ============================================
DB_HOST={"localhost" if env_type == "development" else "postgres"}
DB_PORT=5432
DB_USER=aurumai
DB_PASSWORD={db_password}
DB_NAME={"aurumai_dev" if env_type == "development" else "aurumai"}

# ============================================
# TimescaleDB Configuration
# ============================================
TSDB_HOST={"localhost" if env_type == "development" else "timescaledb"}
TSDB_PORT=5432
TSDB_USER=aurumai
TSDB_PASSWORD={db_password}
TSDB_NAME={"aurumai_timeseries_dev" if env_type == "development" else "aurumai_timeseries"}

# ============================================
# MQTT Broker Configuration
# ============================================
MQTT_BROKER_HOST={"localhost" if env_type == "development" else "mosquitto"}
MQTT_BROKER_PORT=1883
MQTT_USERNAME=aurumai
MQTT_PASSWORD={mqtt_password}

# ============================================
# CORS Configuration
# ============================================
CORS_ORIGINS=http://localhost:3000{"" if env_type == "development" else ",https://yourdomain.com"}

# ============================================
# Observability
# ============================================
PROMETHEUS_ENABLED=true
TRACING_ENABLED={"false" if env_type == "development" else "true"}
TRACING_SERVICE_NAME=aurumai-backend
TRACING_OTLP_ENDPOINT={"" if env_type == "development" else "http://tempo:4317"}

# ============================================
# Feature Flags
# ============================================
FEATURE_PREDICTIVE=true
FEATURE_CARBON=true
FEATURE_ENERGY=true
FEATURE_WATER=false
FEATURE_ANALYTICS=true
"""
    return template


def main():
    """Main function to generate and display secrets."""
    parser = argparse.ArgumentParser(
        description="Generate secure keys and passwords for AurumAI Platform"
    )
    parser.add_argument(
        "--length",
        type=int,
        default=32,
        help="Length of the secret key (default: 32)"
    )
    parser.add_argument(
        "--env",
        type=str,
        choices=["development", "staging", "production"],
        default="development",
        help="Environment type (default: development)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save to .env.{env} file"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔐 AurumAI Platform - Secret Key Generator")
    print("=" * 60)
    print()
    
    # Generate individual secrets
    secret_key = generate_secret_key(args.length)
    db_password = generate_password(20)
    mqtt_password = generate_password(16)
    
    print(f"Environment: {args.env}")
    print()
    print("Generated Secrets:")
    print("-" * 60)
    print(f"SECRET_KEY:     {secret_key}")
    print(f"DB_PASSWORD:    {db_password}")
    print(f"MQTT_PASSWORD:  {mqtt_password}")
    print("-" * 60)
    print()
    
    # Generate full .env template
    env_content = create_env_template(args.env)
    
    if args.save:
        env_file = Path(f".env.{args.env}")
        
        if env_file.exists():
            response = input(f"⚠️  {env_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("❌ Cancelled. File not modified.")
                return
        
        env_file.write_text(env_content)
        print(f"✅ Saved to {env_file}")
        print()
        print("⚠️  IMPORTANT:")
        print(f"   1. Review {env_file} and adjust settings as needed")
        print(f"   2. Copy to .env for local development:")
        print(f"      cp {env_file} backend/.env")
        print(f"   3. NEVER commit .env files to git!")
        print()
    else:
        print("Full .env template:")
        print("=" * 60)
        print(env_content)
        print("=" * 60)
        print()
        print("💡 Tip: Use --save to write to .env.{env} file")
        print("   Example: python tools/generate_secrets.py --env production --save")
    
    print()
    print("🔒 Security Reminders:")
    print("   • Store production secrets in a secure vault (AWS/GCP/Azure)")
    print("   • Rotate secrets periodically (every 90 days recommended)")
    print("   • Use different secrets for each environment")
    print("   • Never share secrets via email or chat")
    print()


if __name__ == "__main__":
    main()
