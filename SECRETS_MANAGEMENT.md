# 🔐 SECRETS MANAGEMENT - SECURITY GUIDE

## ⚠️ CRITICAL SECURITY CHANGES

Este repositorio ha sido **endurecido** para prevenir exposición de secretos. Todos los secretos hardcoded han sido removidos.

---

## 📋 CAMBIOS IMPLEMENTADOS

### ✅ **1. Variables Requeridas (No Defaults Inseguros)**

Las siguientes variables **NO tienen valores por defecto** y causarán un `ValidationError` si no se proveen:

- `DB_PASSWORD` - Contraseña de PostgreSQL
- `TSDB_PASSWORD` - Contraseña de TimescaleDB
- `MQTT_PASSWORD` - Contraseña de MQTT broker
- `SECRET_KEY` - Clave secreta para JWT/sessions (mínimo 32 chars)

**Antes (INSEGURO):**

```python
db_password: str = "aurumai_dev_password"  # ❌ Hardcoded
secret_key: str = "your-secret-key..."     # ❌ Inseguro
```

**Ahora (SEGURO):**

```python
db_password: str = Field(..., description="Database password (REQUIRED)")
secret_key: str = Field(..., min_length=32, description="Secret key (REQUIRED)")
```

### ✅ **2. Validaciones de Producción**

Se agregaron validadores que previenen configuraciones inseguras:

```python
@field_validator("secret_key")
def validate_secret_key(cls, v: str, info) -> str:
    """En producción: SECRET_KEY debe tener mínimo 64 caracteres"""
    if info.data.get("environment") == "production":
        if len(v) < 64:
            raise ValueError("SECRET_KEY too short for production")
    return v

@field_validator("debug")
def validate_debug_in_production(cls, v: bool, info) -> bool:
    """DEBUG debe ser False en producción"""
    if info.data.get("environment") == "production" and v:
        raise ValueError("DEBUG must be False in production")
    return v
```

### ✅ **3. Docker Compose Sin Hardcoded Secrets**

**Antes (INSEGURO):**

```yaml
environment:
  - POSTGRES_PASSWORD=aurumai_pass # ❌ Hardcoded en git
```

**Ahora (SEGURO):**

```yaml
env_file:
  - .env # Lee de archivo externo
environment:
  - POSTGRES_PASSWORD=${DB_PASSWORD:?DB_PASSWORD is required}
```

### ✅ **4. .gitignore Actualizado**

```gitignore
# CRITICAL: Never commit real secrets
.env
.env.local
.env.production
.env.staging
.env.test
!.env.example        # Template público
!.env.development    # Safe defaults para desarrollo
```

---

## 🚀 QUICK START - DESARROLLO

### **1. Copiar Template de Variables**

```bash
# Opción A: Usar .env.development (recomendado)
cp .env.development .env

# Opción B: Usar .env.example y llenar valores
cp .env.example .env
```

### **2. Revisar y Actualizar .env**

Edita `.env` y actualiza las variables críticas:

```bash
# Generar SECRET_KEY fuerte
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Actualizar en .env
SECRET_KEY=<PEGAR_KEY_GENERADA>
DB_PASSWORD=<TU_PASSWORD_SEGURO>
```

### **3. Validar Configuración**

```bash
cd backend

# Activar virtualenv
source .venv/bin/activate

# Test: Cargar settings (debe funcionar sin errores)
python -c "from infrastructure.config.settings import settings; print(settings.app_name)"
```

**Salida esperada:**

```
AurumAI Platform
```

**Si falta una variable REQUIRED:**

```
Error cargando configuración: 1 validation error for Settings
db_password
  Field required [type=missing, input_value={...}, input_type=dict]
```

---

## 🏭 PRODUCCIÓN

### **1. Generar Secretos Fuertes**

```bash
# SECRET_KEY (64+ caracteres)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"

# DB_PASSWORD (32+ caracteres, alfanumérico + símbolos)
python -c "import secrets; print('DB_PASSWORD=' + secrets.token_urlsafe(32))"

# MQTT_PASSWORD
python -c "import secrets; print('MQTT_PASSWORD=' + secrets.token_urlsafe(32))"
```

### **2. Crear .env.production**

```bash
# NO versionar este archivo
cat > .env.production << EOF
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<GENERAR_CON_COMANDO_ARRIBA>
DB_PASSWORD=<GENERAR_CON_COMANDO_ARRIBA>
TSDB_PASSWORD=<GENERAR_CON_COMANDO_ARRIBA>
MQTT_PASSWORD=<GENERAR_CON_COMANDO_ARRIBA>
# ... resto de variables
EOF

# Asegurar permisos restrictivos
chmod 600 .env.production
```

### **3. Usar Secrets Manager (Recomendado)**

Para producción real, considerar:

**AWS Secrets Manager:**

```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='aurumai/prod/db-password')
```

**HashiCorp Vault:**

```bash
export DB_PASSWORD=$(vault kv get -field=password secret/aurumai/db)
```

**Kubernetes Secrets:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aurumai-secrets
type: Opaque
data:
  db-password: <base64-encoded>
```

---

## 🔍 VERIFICACIÓN DE SEGURIDAD

### **Checklist Pre-Deploy:**

- [ ] ✅ `.env` NO está commiteado en git
- [ ] ✅ `.env.production` tiene secretos fuertes (64+ chars)
- [ ] ✅ `SECRET_KEY` generado con `secrets.token_urlsafe(64)`
- [ ] ✅ `DEBUG=false` en producción
- [ ] ✅ Passwords NO reutilizados entre entornos
- [ ] ✅ `docker-compose.yml` usa `${ENV_VARS}`, NO hardcoded
- [ ] ✅ Archivo `.env` tiene permisos `600` (solo owner lee/escribe)

### **Validar Configuración:**

```bash
# 1. Backend settings válidos
cd backend
python -c "from infrastructure.config.settings import settings; \
    assert settings.secret_key != 'your-secret-key-change-in-production'; \
    assert len(settings.secret_key) >= 32; \
    print('✅ Settings OK')"

# 2. Docker Compose resuelve variables
docker-compose config | grep -i password
# NO debería mostrar passwords hardcoded

# 3. Verificar .env NO está en git
git ls-files | grep -E "^\.env$"
# NO debería retornar nada
```

---

## 🐛 TROUBLESHOOTING

### **Error: "Field required" al iniciar backend**

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
db_password
  Field required [type=missing, input_value={...}]
```

**Solución:**

1. Verificar que `.env` existe: `ls -la .env`
2. Verificar que contiene `DB_PASSWORD=...`: `grep DB_PASSWORD .env`
3. Si usas Docker: Verificar `env_file: - .env` en `docker-compose.yml`

### **Error: "SECRET_KEY too short for production"**

```
ValueError: SECRET_KEY must be at least 64 characters in production
```

**Solución:**

```bash
# Generar nueva SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Actualizar en .env.production
SECRET_KEY=<NUEVA_KEY_64_CHARS>
```

### **Error: "DEBUG must be False in production"**

```
ValueError: DEBUG must be False in production environment
```

**Solución:**

```bash
# En .env.production
ENVIRONMENT=production
DEBUG=false  # Cambiar a false
```

---

## 📚 ARCHIVOS DE CONFIGURACIÓN

| Archivo            | Propósito                     | Commitear a Git |
| ------------------ | ----------------------------- | --------------- |
| `.env.example`     | Template con documentación    | ✅ SÍ           |
| `.env.development` | Defaults seguros para dev     | ✅ SÍ           |
| `.env`             | Variables de desarrollo local | ❌ NO           |
| `.env.production`  | Variables de producción       | ❌ NO           |
| `.env.staging`     | Variables de staging          | ❌ NO           |

---

## 🔗 RECURSOS

- **Generar Secretos:** [Python secrets module](https://docs.python.org/3/library/secrets.html)
- **Pydantic Settings:** [Pydantic Settings Docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Docker Secrets:** [Docker Secrets Guide](https://docs.docker.com/engine/swarm/secrets/)
- **OWASP Secrets Management:** [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

---

## ✅ RESUMEN DE CAMBIOS

| Archivo                                     | Cambio                              | Impacto            |
| ------------------------------------------- | ----------------------------------- | ------------------ |
| `backend/infrastructure/config/settings.py` | Passwords/secrets ahora REQUIRED    | ⚠️ Breaking change |
| `.env.example`                              | Template completo con documentación | ✅ Mejora          |
| `.env.development`                          | Defaults seguros para dev           | ✅ Nuevo           |
| `docker-compose.yml`                        | Usa `env_file` + `${VARS}`          | 🔒 Seguro          |
| `.gitignore`                                | Ignora `.env*` excepto templates    | 🔒 Seguro          |

**¿Preguntas?** Revisa este documento o consulta `backend/infrastructure/config/settings.py` para ver validaciones completas.
