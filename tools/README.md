# 🛠️ Tools Directory

This directory contains utility scripts and tools for the AurumAI platform.

## 📋 Available Tools

### 1. `generate_secrets.py` - Secret Key Generator

**Purpose:** Generate cryptographically secure keys and passwords for different environments.

**Features:**

- ✅ Generates URL-safe SECRET_KEY using Python's `secrets` module
- ✅ Creates strong passwords with mixed characters
- ✅ Supports multiple environments (development, staging, production)
- ✅ Can generate complete `.env` templates
- ✅ Includes security best practices and reminders

**Usage:**

```bash
# Basic usage - Display secrets only
python3 tools/generate_secrets.py

# Generate for specific environment
python3 tools/generate_secrets.py --env production

# Generate and save to file
python3 tools/generate_secrets.py --env production --save

# Custom key length
python3 tools/generate_secrets.py --length 64
```

**Options:**

- `--length N`: Length of the SECRET_KEY (default: 32)
- `--env ENV`: Environment type: development, staging, production (default: development)
- `--save`: Save generated .env template to `.env.{env}` file

**Examples:**

```bash
# Generate secrets for development
python3 tools/generate_secrets.py --env development --save

# Generate for production with longer key
python3 tools/generate_secrets.py --env production --length 64 --save

# Just display secrets without saving
python3 tools/generate_secrets.py --env production
```

**Output:**

The tool generates:

1. **SECRET_KEY**: URL-safe base64 encoded string (default 32 chars)
2. **DB_PASSWORD**: Strong password for PostgreSQL (20 chars)
3. **MQTT_PASSWORD**: Strong password for MQTT broker (16 chars)
4. **Complete .env template** with all necessary configuration

**Security Notes:**

⚠️ **CRITICAL SECURITY REMINDERS:**

1. **Never commit `.env` files to git**

   - Add to `.gitignore`: `*.env*` (except `.env.example`)
   - Keep `.env.example` with placeholder values only

2. **Use different secrets for each environment**

   - Development: Less critical, can be simpler
   - Staging: Should match production security level
   - Production: Maximum security, stored in vault

3. **Store production secrets securely**

   - AWS: AWS Secrets Manager or Parameter Store
   - GCP: Google Secret Manager
   - Azure: Azure Key Vault
   - HashiCorp: Vault
   - Docker: Docker Secrets (Swarm mode)

4. **Rotate secrets periodically**

   - Recommended: Every 90 days
   - After security incidents: Immediately
   - When team members leave: Within 24 hours

5. **Never share secrets via:**
   - Email
   - Chat (Teams, Discord)
   - Screenshots
   - Video recordings
   - Public repositories

**Integration with Backend:**

The backend uses these secrets via environment variables:

```python
# backend/infrastructure/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str  # Used for JWT signing, session management
    db_password: str  # PostgreSQL authentication
    mqtt_password: str  # MQTT broker authentication

    class Config:
        env_file = ".env"
```

**Testing Generated Secrets:**

```bash
# 1. Generate secrets
python3 tools/generate_secrets.py --env development --save

# 2. Copy to backend directory
cp .env.development backend/.env

# 3. Test backend loads configuration
cd backend
python3 -c "from infrastructure.config.settings import get_settings; print(get_settings().secret_key[:10] + '...')"

# Expected output: First 10 chars of SECRET_KEY followed by "..."
```

---

## 🔐 Security Best Practices

### Key Generation Standards

**SECRET_KEY Requirements:**

- ✅ Minimum 32 characters (256 bits)
- ✅ Use cryptographically secure random generator (`secrets` module)
- ✅ URL-safe base64 encoding
- ❌ Never use predictable values (e.g., "secret123", "password")
- ❌ Never reuse keys across environments

**Password Requirements:**

- ✅ Minimum 16 characters
- ✅ Mix of uppercase, lowercase, digits, and symbols
- ✅ Generated using cryptographically secure random
- ❌ No dictionary words
- ❌ No sequential patterns (e.g., "abc123", "qwerty")

### Environment-Specific Considerations

#### Development Environment

```bash
# Can use simpler secrets for local development
python3 tools/generate_secrets.py --env development --save
cp .env.development backend/.env
```

**Characteristics:**

- Less critical secrets (local only)
- Can be stored in project (excluded from git)
- Team can share same dev secrets
- Simplified CORS, logging enabled

#### Production Environment

```bash
# Use maximum security for production
python3 tools/generate_secrets.py --env production --save
```

**Characteristics:**

- Maximum security secrets
- Stored in cloud secret manager (AWS/GCP/Azure)
- Never stored in files committed to git
- Injected via CI/CD pipeline
- Rotated every 90 days
- Logged access and usage

### Secret Management Workflow

**Step 1: Generate Secrets**

```bash
python3 tools/generate_secrets.py --env production --save
```

**Step 2: Store in Vault (Production)**

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
    --name aurumai/production/secret-key \
    --secret-string "$(grep SECRET_KEY .env.production | cut -d '=' -f2)"

# GCP Secret Manager
echo -n "$(grep SECRET_KEY .env.production | cut -d '=' -f2)" | \
    gcloud secrets create aurumai-secret-key --data-file=-

# Azure Key Vault
az keyvault secret set \
    --vault-name aurumai-vault \
    --name secret-key \
    --value "$(grep SECRET_KEY .env.production | cut -d '=' -f2)"
```

**Step 3: Delete Local Copies**

```bash
# CRITICAL: Remove .env.production after storing in vault
shred -u .env.production  # Linux
srm .env.production  # macOS (if srm installed)
rm -P .env.production  # macOS alternative
```

**Step 4: Configure CI/CD**

```yaml
# .github/workflows/deploy.yml
- name: Get secrets from vault
  env:
    SECRET_KEY: ${{ secrets.SECRET_KEY }} # From GitHub Secrets
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

---

## 📚 Additional Resources

- [Python secrets module documentation](https://docs.python.org/3/library/secrets.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)

---

## 🆘 Troubleshooting

**Issue:** `ImportError: No module named 'secrets'`

- **Solution:** Ensure Python 3.6+ is installed (`secrets` is in stdlib since 3.6)

**Issue:** Generated .env file not working

- **Solution:** Check file location - should be in `backend/.env`, not root

**Issue:** Backend not loading SECRET_KEY

- **Solution:** Verify `.env` file exists and has `SECRET_KEY=...` line without quotes

**Issue:** "Secret already exists" in cloud vault

- **Solution:** Use update command instead of create, or delete old secret first

---

## 📝 Changelog

### v1.0.0 (2025-11-16)

- ✨ Initial release of `generate_secrets.py`
- ✅ Support for development, staging, production environments
- ✅ Generates SECRET_KEY, DB_PASSWORD, MQTT_PASSWORD
- ✅ Complete .env template generation
- ✅ Security best practices documentation
