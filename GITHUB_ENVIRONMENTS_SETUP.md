# GitHub Environments Setup

## 📋 Resumen

Este documento explica cómo configurar GitHub Environments para habilitar los deploys automáticos del workflow CI/CD.

---

## ⚠️ Estado Actual

- **CI/CD Pipeline:** ✅ Configurado (9 jobs activos)
- **Deploy a Staging:** ⏸️ Comentado temporalmente
- **Razón:** Environment 'staging' no existe en GitHub repo

---

## 🎯 ¿Qué es un GitHub Environment?

Los **Environments** en GitHub Actions permiten:

1. **Configurar URLs de deployment** (ej: `https://staging.aurumai.com`)
2. **Protection Rules:**
   - Requerir aprobaciones manuales antes de deploy
   - Restringir qué branches pueden deployar
   - Configurar timeouts de espera
3. **Secrets específicos por environment:**
   - `STAGING_API_KEY`
   - `PRODUCTION_DB_PASSWORD`
   - etc.

---

## 🚀 Cómo Crear el Environment 'staging'

### Paso 1: Acceder a Settings

1. Ve a tu repositorio: https://github.com/Neiland85-Org/aurumai-mockup
2. Haz clic en **Settings** (tab superior)
3. En el menú lateral izquierdo, busca **Environments**

### Paso 2: Crear el Environment

1. Haz clic en **New environment**
2. **Name:** `staging`
3. Haz clic en **Configure environment**

### Paso 3: Configurar (Opcional)

#### **Deployment Protection Rules:**

- **Required reviewers:**

  - Marca esta opción si quieres aprobación manual antes de deploy
  - Selecciona usuarios/equipos que pueden aprobar
  - Útil para: Control de cambios, compliance, auditoría

- **Wait timer:**

  - Retraso antes de deploy (0-43,200 minutos)
  - Útil para: Pausas programadas, ventanas de mantenimiento

- **Deployment branches:**
  - Por defecto: Cualquier branch
  - Recomendado: Solo `main` y `develop`
  - Protege contra deploys accidentales

#### **Environment Secrets:**

Puedes agregar secrets específicos para staging:

```
GCP_SA_KEY_STAGING
STAGING_DATABASE_URL
STAGING_API_KEY
RAILWAY_TOKEN_STAGING
```

**Nota:** Estos secrets solo están disponibles cuando el workflow usa este environment.

### Paso 4: Guardar

Haz clic en **Save protection rules**

---

## 🔓 Habilitar Deploy en Workflow

Una vez creado el environment, descomenta el job `deploy-staging` en `.github/workflows/ci.yml`:

### Ubicación del código:

Busca la sección:

```yaml
# ============================================
# DEPLOY TO STAGING
# ============================================
# NOTA: Deploy comentado temporalmente...
# deploy-staging:
#   name: 🚀 Deploy to Staging
#   ...
```

### Cambio requerido:

```yaml
# ANTES (comentado):
# deploy-staging:
#   name: 🚀 Deploy to Staging

# DESPUÉS (activo):
deploy-staging:
  name: 🚀 Deploy to Staging
```

**⚠️ IMPORTANTE:** Descomenta **TODO** el job, no solo la primera línea.

---

## 🎨 Configuración Recomendada por Environment

### **Staging Environment:**

```yaml
Name: staging
URL: https://staging-aurumai.railway.app (o tu URL real)

Protection Rules:
  - Required reviewers: ❌ No (auto-deploy)
  - Wait timer: 0 minutos
  - Deployment branches: main, develop

Secrets:
  - RAILWAY_TOKEN_STAGING
  - STAGING_DATABASE_URL
  - STAGING_MQTT_PASSWORD
```

### **Production Environment (futuro):**

```yaml
Name: production
URL: https://aurumai.com

Protection Rules:
  - Required reviewers: ✅ Sí (tu usuario)
  - Wait timer: 5 minutos
  - Deployment branches: Solo main

Secrets:
  - RAILWAY_TOKEN_PRODUCTION
  - PRODUCTION_DATABASE_URL
  - PRODUCTION_MQTT_PASSWORD
  - GCP_SA_KEY_PRODUCTION
```

---

## 📊 Flujo de Trabajo Completo

### Con Environment Configurado:

```
1. Push a main/develop
   ↓
2. GitHub Actions inicia CI/CD
   ↓
3. Ejecuta: lint, security, tests (paralelo)
   ↓
4. Build: Docker images
   ↓
5. Publica: GitHub Container Registry
   ↓
6. Deploy: Espera aprobación (si configurado)
   ↓
7. Deploy: Cloud Run / Railway
   ↓
8. Smoke Tests: Verifica health endpoints
   ↓
9. Notificación: Email (si configurado)
```

### Sin Environment (Estado Actual):

```
1. Push a main/develop
   ↓
2. GitHub Actions inicia CI/CD
   ↓
3. Ejecuta: lint, security, tests (paralelo)
   ↓
4. Build: Docker images
   ↓
5. Publica: GitHub Container Registry
   ↓
6. ✅ TERMINA (deploy comentado)
```

---

## 🔧 Configuración Adicional para Deploy

### **Opción 1: Railway Deploy**

1. Crea cuenta en Railway.app
2. Conecta repo de GitHub
3. Crea proyecto "aurumai-staging"
4. Genera token: Settings → Tokens → Create Token
5. Agrega secret en GitHub:

   - Settings → Secrets → Actions
   - Name: `RAILWAY_TOKEN_STAGING`
   - Value: (tu token)

6. Actualiza workflow para usar Railway CLI:

```yaml
- name: Deploy to Railway
  run: |
    npm i -g @railway/cli
    railway up --service backend --environment staging
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN_STAGING }}
```

### **Opción 2: Google Cloud Run**

1. Crea proyecto en GCP
2. Habilita Cloud Run API
3. Crea Service Account con roles:

   - Cloud Run Admin
   - Storage Admin
   - Service Account User

4. Descarga clave JSON
5. Agrega secret en GitHub:

   - Name: `GCP_SA_KEY_STAGING`
   - Value: (contenido del JSON)

6. Descomenta en workflow:

```yaml
credentials: ${{ secrets.GCP_SA_KEY_STAGING }}
```

---

## ✅ Checklist de Activación

Antes de habilitar deploy, verifica:

- [ ] Docker Desktop instalado localmente
- [ ] Environment 'staging' creado en GitHub
- [ ] Plataforma de deploy elegida (Railway/GCP/Render)
- [ ] Secrets configurados en GitHub
- [ ] URL de staging definida
- [ ] Database staging configurada
- [ ] MQTT broker staging configurado
- [ ] Health endpoints funcionando
- [ ] Smoke tests validados

---

## 🆘 Troubleshooting

### Error: "Environment 'staging' not found"

**Causa:** Environment no existe en GitHub Settings

**Solución:**

1. Settings → Environments → New environment → "staging"
2. Guarda y haz nuevo push

### Error: "Required reviewers not met"

**Causa:** Environment configurado con aprobación requerida

**Solución:**

1. Ve a Actions tab
2. Encuentra el workflow run
3. Haz clic en "Review deployments"
4. Aprueba el deploy

### Error: "GCP credentials invalid"

**Causa:** Secret `GCP_SA_KEY` incorrecto o expirado

**Solución:**

1. Descarga nueva clave de Service Account
2. Actualiza secret en GitHub
3. Re-run workflow

### Workflow se salta el deploy

**Causa:** Condición `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`

**Solución:**

- Deploy solo se ejecuta en push a `main`
- Pull requests NO deployean
- Verifica que estés en branch correcta

---

## 📚 Referencias

- [GitHub Environments Docs](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Cloud Run Deploy Action](https://github.com/google-github-actions/deploy-cloudrun)
- [Railway Deployment Guide](https://docs.railway.app/deploy/deployments)
- [Render Deployment](https://render.com/docs/deploy-from-github)

---

## 🎯 Próximos Pasos

1. **Inmediato:**

   - ✅ Environment 'staging' comentado (hecho)
   - ⏳ Instalar Docker Desktop
   - ⏳ Crear environment en GitHub (cuando estés listo)

2. **Desarrollo:**

   - ⏳ Configurar Railway/GCP
   - ⏳ Agregar secrets
   - ⏳ Descomentar deploy
   - ⏳ Primer deploy a staging

3. **Producción:**
   - ⏳ Environment 'production'
   - ⏳ Protection rules estrictas
   - ⏳ Smoke tests completos
   - ⏳ Monitoreo con Grafana Cloud

---

**Última actualización:** 16 de noviembre de 2025
**Estado:** Deploy temporalmente deshabilitado hasta configurar infrastructure
