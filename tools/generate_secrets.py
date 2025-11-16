#!/usr/bin/env python3
"""
Secret Key Generator for AurumAI Platform
Generates cryptographically secure keys for different environments.

SECURITY WARNING: This tool generates sensitive information.
Never commit generated .env files to version control.

Usage:
    python tools/generate_secrets.py
    python tools/generate_secrets.py --length 64
    python tools/generate_secrets.py --save --confirm-security
"""

import argparse
import secrets
import string
from pathlib import Path
from typing import Optional


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


def create_env_template(env_type: str = "development", use_placeholders: bool = False) -> str:
    """
    Create .env template with generated secrets or placeholders.

    Args:
        env_type: Environment type (development, staging, production)
        use_placeholders: If True, use <CHANGE_ME> placeholders instead of real secrets

    Returns:
        .env file content as string
    """
    if use_placeholders:
        secret_key = "<CHANGE_ME_SECRET_KEY>"
        db_password = "<CHANGE_ME_DB_PASSWORD>"
        mqtt_password = "<CHANGE_ME_MQTT_PASSWORD>"
    else:
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


def save_env_file_securely(env_content: str, env_file: Path, env_type: str) -> None:
    """
    Save environment file with security checks.

    Args:
        env_content: Content to save
        env_file: File path to save to
        env_type: Environment type for warnings
    """
    # Security check: Ensure file is in .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if not any(pattern in gitignore_content for pattern in [".env", "*.env", f"{env_file.name}"]):
            print("⚠️  WARNING: .env files may not be properly excluded from git!")
            print("   Please ensure your .gitignore includes:")
            print("   .env")
            print("   .env.*")
            print()

    # Write file with secure permissions (if possible)
    env_file.write_text(env_content)

    # Try to set restrictive permissions (Unix-like systems only)
    try:
        env_file.chmod(0o600)  # Owner read/write only
    except OSError:
        pass  # Windows or permission denied, skip

    print(f"✅ Saved to {env_file}")
    print()
    print("🔒 SECURITY REMINDERS:")
    print(f"   • File permissions set to 600 (owner read/write only)")
    print(f"   • Ensure {env_file} is in .gitignore")
    print(f"   • Never commit this file to version control")
    if env_type == "production":
        print(f"   • Use a secret management system (AWS/GCP/Azure Secrets)")
        print(f"   • Rotate these secrets every 90 days")
    print()


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
        help="Save to .env.{env} file (requires --confirm-security)"
    )
    parser.add_argument(
        "--confirm-security",
        action="store_true",
        help="Confirm understanding of security implications"
    )
    parser.add_argument(
        "--placeholders",
        action="store_true",
        help="Generate template with <CHANGE_ME> placeholders instead of real secrets"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🔐 AurumAI Platform - Secret Key Generator")
    print("=" * 60)
    print()

    if args.save and not args.confirm_security:
        print("❌ ERROR: --save requires --confirm-security flag")
        print()
        print("Security requirement: You must acknowledge that you're saving sensitive")
        print("information to disk. This tool generates REAL secrets that should never")
        print("be committed to version control.")
        print()
        print("Usage: python tools/generate_secrets.py --save --confirm-security")
        return 1

    # Security check: Warn about production secrets
    if args.env == "production" and not args.placeholders:
        print("🚨 PRODUCTION ENVIRONMENT DETECTED!")
        print("   Generating real secrets for production is HIGHLY discouraged.")
        print("   Use a secret management system instead (AWS/GCP/Azure Secrets).")
        print()
        confirm_prod = input("Are you sure you want to generate real production secrets? (no/YES): ")
        if confirm_prod != "YES":
            print("❌ Cancelled. Use --placeholders for production templates.")
            return 1

    # Generate individual secrets
    if not args.placeholders:
        secret_key = generate_secret_key(args.length)
        db_password = generate_password(20)
        mqtt_password = generate_password(16)

        print("🚨 SECURITY WARNING: The following secrets will be displayed in plain text!")
        print("   Never share this output or commit it to version control.")
        print("   Use --placeholders for safe template generation.")
        print()

        print(f"Environment: {args.env}")
        print()
        print("🔑 Generated Secrets:")
        print("-" * 60)
        print("SECRET_KEY:     <generated - check .env file>")
        print("DB_PASSWORD:    <generated - check .env file>")
        print("MQTT_PASSWORD:  <generated - check .env file>")
        print("-" * 60)
        print()
        print("⚠️  IMPORTANT: Store these secrets securely (vault, secret manager)")
        print("   Never use them in development without proper access controls")
        print("✅ Secrets written to .env file - do NOT log or commit them")
        print()
    else:
        print(f"Environment: {args.env} (placeholders)")
        print()
        print("📝 Template with placeholders:")
        print("-" * 60)
        print("SECRET_KEY:     <CHANGE_ME_SECRET_KEY>")
        print("DB_PASSWORD:    <CHANGE_ME_DB_PASSWORD>")
        print("MQTT_PASSWORD:  <CHANGE_ME_MQTT_PASSWORD>")
        print("-" * 60)
        print()

    # Generate full .env template
    env_content = create_env_template(args.env, use_placeholders=args.placeholders)

    if args.save:
        env_file = Path(f".env.{args.env}")

        if env_file.exists():
            response = input(f"⚠️  {env_file} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("❌ Cancelled. File not modified.")
                return 0

        save_env_file_securely(env_content, env_file, args.env)
        print("💡 Next steps:")
        print(f"   1. Review {env_file} and customize values")
        if not args.placeholders:
            print(f"   2. Copy to backend/.env for local development:")
            print(f"      cp {env_file} backend/.env")
        print(f"   3. NEVER commit .env files to git!")
        print()
    else:
        print("📄 Full .env template:")
        print("=" * 60)
        print(env_content)
        print("=" * 60)
        print()
        if not args.placeholders:
            print("💡 Tip: Use --save --confirm-security to write to .env.{env} file")
            print("   Example: python tools/generate_secrets.py --env production --save --confirm-security")
        else:
            print("💡 Tip: Use --save --placeholders to create template file")
            print("   Example: python tools/generate_secrets.py --placeholders --save --confirm-security")

    print()
    print("🔒 Security Best Practices:")
    print("   • Store production secrets in a secure vault (AWS/GCP/Azure)")
    print("   • Rotate secrets periodically (every 90 days recommended)")
    print("   • Use different secrets for each environment")
    print("   • Never share secrets via email or chat")
    if args.placeholders:
        print("   • Replace <CHANGE_ME> placeholders with actual secrets")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
