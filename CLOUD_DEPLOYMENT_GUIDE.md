# ☁️ Cloud Deployment Guide - AurumAI Platform

**Fecha:** 15 de noviembre de 2025  
**Versión:** 1.0.0

---

## 📋 Resumen Ejecutivo

Esta guía documenta **3 opciones de deployment cloud** para AurumAI Platform cuando Docker esté configurado localmente.

### Opciones Disponibles

1. **Railway** - Más fácil, deploy automático desde GitHub
2. **Google Cloud Run** - Serverless, auto-scaling, pay-per-use
3. **Render** - Alternativa simple, free tier disponible

---

## 🚂 Opción 1: Railway (Recomendado para Inicio)

### Características

- ✅ **Deploy automático** desde GitHub
- ✅ **Free tier:** $5/mes crédito
- ✅ **PostgreSQL incluido**
- ✅ **Variables de entorno** fácil configuración
- ✅ **SSL automático**
- ⏱️ **Setup:** 10-15 minutos

### Pre-requisitos

```bash
# Verificar que Docker esté instalado
docker --version

# Verificar que el código esté en GitHub
git remote -v
```

### Paso 1: Crear Cuenta en Railway

1. Ir a https://railway.app
2. Sign up con GitHub
3. Conectar repositorio `aurumai-mockup`

### Paso 2: Crear Proyecto Backend

```bash
# En Railway Dashboard:
1. New Project → Deploy from GitHub repo
2. Seleccionar: Neiland85-Org/aurumai-mockup
3. Root Directory: /backend
4. Dockerfile: Dockerfile.prod
```

### Paso 3: Añadir PostgreSQL

```bash
# En Railway:
1. Add Plugin → PostgreSQL
2. Copy connection string
3. Guardar para configuración
```

### Paso 4: Configurar Variables de Entorno

```bash
# En Railway Project → Variables:

# Database (auto-generadas por Railway PostgreSQL plugin)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# App
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# TimescaleDB (usar mismo PostgreSQL por ahora)
TSDB_HOST=${{Postgres.PGHOST}}
TSDB_PORT=${{Postgres.PGPORT}}
TSDB_USER=${{Postgres.PGUSER}}
TSDB_PASSWORD=${{Postgres.PGPASSWORD}}
TSDB_NAME=${{Postgres.PGDATABASE}}

# MQTT (CloudMQTT o HiveMQ Cloud)
MQTT_BROKER_HOST=mqtt.railway.example.com
MQTT_PORT=1883
MQTT_USERNAME=aurumai_prod
MQTT_PASSWORD=<CHANGE_ME>

# Security
SECRET_KEY=<GENERATE_WITH_python_-c_import_secrets_print_secrets_token_urlsafe_64>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Observability
ENABLE_TRACING=true
ENABLE_METRICS=true
ENABLE_LOGGING=true
LOG_FORMAT=json

# CORS (añadir dominio de Railway cuando se genere)
CORS_ORIGINS=["https://your-app.railway.app"]
```

### Paso 5: Deploy

```bash
# Railway auto-deploya cuando detecta cambios en main
# O forzar deploy manual:
1. Railway Dashboard → Deploy
2. Ver logs en tiempo real
3. Verificar que el servicio esté UP
```

### Paso 6: Configurar Frontend

```bash
# Crear nuevo servicio en Railway:
1. Add Service → GitHub Repo
2. Root Directory: /frontend
3. Dockerfile: Dockerfile.prod

# Variables de entorno Frontend:
NEXT_PUBLIC_API_URL=https://backend-aurumai.railway.app
NODE_ENV=production
```

### Paso 7: Health Check

```bash
# Verificar backend
curl https://backend-aurumai.railway.app/health

# Verificar API
curl https://backend-aurumai.railway.app/api/v1/health

# Expected:
# {"status":"ok","version":"0.1.0"}
```

### Paso 8: Configurar Dominio Personalizado (Opcional)

```bash
# En Railway:
1. Settings → Domains
2. Add Custom Domain
3. Configurar DNS:
   - Type: CNAME
   - Name: api (o app)
   - Value: <railway-generated-url>
```

### Costos Railway

```
Free Tier:
- $5/mes crédito
- Suficiente para desarrollo/staging

Hobby Plan:
- $20/mes
- 100GB transfer
- PostgreSQL incluido

Pro Plan:
- $50/mes
- 500GB transfer
- Priority support
```

---

## ☁️ Opción 2: Google Cloud Run (Escalable)

### Características

- ✅ **Serverless** - Auto-scaling 0 → N instancias
- ✅ **Pay-per-use** - Solo pagas cuando hay tráfico
- ✅ **Free tier:** 2M requests/mes
- ✅ **Integración con Cloud SQL**
- ⏱️ **Setup:** 20-30 minutos

### Pre-requisitos

```bash
# Instalar Google Cloud SDK
brew install --cask google-cloud-sdk

# Iniciar sesión
gcloud auth login

# Crear proyecto
gcloud projects create aurumai-prod --name="AurumAI Production"
gcloud config set project aurumai-prod

# Habilitar APIs necesarias
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Paso 1: Configurar Container Registry

```bash
# Habilitar Artifact Registry
gcloud services enable artifactregistry.googleapis.com

# Crear repositorio
gcloud artifacts repositories create aurumai-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="AurumAI Docker images"

# Configurar Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### Paso 2: Build y Push Imagen

```bash
# Build backend image
cd backend
docker build -f Dockerfile.prod -t backend:latest .

# Tag para GCP
docker tag backend:latest \
  us-central1-docker.pkg.dev/aurumai-prod/aurumai-repo/backend:latest

# Push
docker push us-central1-docker.pkg.dev/aurumai-prod/aurumai-repo/backend:latest
```

### Paso 3: Crear Cloud SQL (PostgreSQL)

```bash
# Crear instancia
gcloud sql instances create aurumai-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Crear database
gcloud sql databases create aurumai_prod \
  --instance=aurumai-db

# Crear usuario
gcloud sql users set-password aurumai_admin \
  --instance=aurumai-db \
  --password=<STRONG_PASSWORD>
```

### Paso 4: Configurar Secrets

```bash
# Crear secrets
echo -n "postgresql://user:pass@/cloudsql/project:region:instance/db" | \
  gcloud secrets create db-url --data-file=-

echo -n "<GENERATE_SECRET_KEY>" | \
  gcloud secrets create secret-key --data-file=-

echo -n "<MQTT_PASSWORD>" | \
  gcloud secrets create mqtt-password --data-file=-
```

### Paso 5: Deploy a Cloud Run

```bash
# Deploy backend
gcloud run deploy aurumai-backend \
  --image us-central1-docker.pkg.dev/aurumai-prod/aurumai-repo/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,LOG_LEVEL=INFO \
  --set-secrets DB_PASSWORD=db-url:latest,SECRET_KEY=secret-key:latest \
  --add-cloudsql-instances aurumai-prod:us-central1:aurumai-db \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80

# Deploy frontend
cd ../frontend
docker build -f Dockerfile.prod -t frontend:latest .

docker tag frontend:latest \
  us-central1-docker.pkg.dev/aurumai-prod/aurumai-repo/frontend:latest

docker push us-central1-docker.pkg.dev/aurumai-prod/aurumai-repo/frontend:latest

gcloud run deploy aurumai-frontend \
  --image us-central1-docker.pkg.dev/aurumai-prod/aurumai-repo/frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=https://aurumai-backend-xxx.run.app \
  --memory 256Mi \
  --cpu 1
```

### Paso 6: Configurar Dominio Personalizado

```bash
# Mapear dominio
gcloud run domain-mappings create \
  --service aurumai-backend \
  --domain api.aurumai.com \
  --region us-central1

gcloud run domain-mappings create \
  --service aurumai-frontend \
  --domain app.aurumai.com \
  --region us-central1
```

### Paso 7: CI/CD con Cloud Build

```yaml
# cloudbuild.yaml
steps:
  # Build backend
  - name: "gcr.io/cloud-builders/docker"
    args:
      - "build"
      - "-f"
      - "backend/Dockerfile.prod"
      - "-t"
      - "us-central1-docker.pkg.dev/$PROJECT_ID/aurumai-repo/backend:$COMMIT_SHA"
      - "backend/"

  # Push backend
  - name: "gcr.io/cloud-builders/docker"
    args:
      - "push"
      - "us-central1-docker.pkg.dev/$PROJECT_ID/aurumai-repo/backend:$COMMIT_SHA"

  # Deploy backend
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk"
    entrypoint: gcloud
    args:
      - "run"
      - "deploy"
      - "aurumai-backend"
      - "--image"
      - "us-central1-docker.pkg.dev/$PROJECT_ID/aurumai-repo/backend:$COMMIT_SHA"
      - "--region"
      - "us-central1"
```

### Costos Cloud Run

```
Free Tier (por mes):
- 2M requests
- 360,000 GB-seconds
- 180,000 vCPU-seconds
- 1GB egress

Ejemplo Staging (bajo tráfico):
- 100K requests/mes
- 512MB RAM × 1 CPU
- Costo estimado: $5-10/mes

Ejemplo Producción (medio tráfico):
- 1M requests/mes
- 1GB RAM × 2 CPU
- Costo estimado: $30-50/mes
```

---

## 🎨 Opción 3: Render (Alternativa Simple)

### Características

- ✅ **Free tier:** PostgreSQL + 750h/mes
- ✅ **Auto-deploy** desde GitHub
- ✅ **SSL automático**
- ✅ **No requiere Docker local** (build en cloud)
- ⏱️ **Setup:** 10 minutos

### Paso 1: Crear Cuenta en Render

1. Ir a https://render.com
2. Sign up con GitHub
3. Conectar repositorio

### Paso 2: Crear PostgreSQL Database

```bash
# En Render Dashboard:
1. New → PostgreSQL
2. Name: aurumai-db
3. Database: aurumai_prod
4. User: aurumai_admin
5. Plan: Free (1GB storage)
6. Create Database

# Copiar:
- Internal Database URL (para backend)
- External Database URL (para migraciones locales)
```

### Paso 3: Crear Backend Service

```bash
# En Render:
1. New → Web Service
2. Connect Repository: aurumai-mockup
3. Name: aurumai-backend
4. Root Directory: backend
5. Environment: Docker
6. Docker Command: (auto-detecta Dockerfile.prod)
7. Plan: Free (512MB RAM, sleep after 15min inactivity)

# Environment Variables:
DATABASE_URL=${{aurumai-db.DATABASE_URL}}
ENVIRONMENT=production
SECRET_KEY=<GENERATE>
MQTT_PASSWORD=<CHANGE_ME>
LOG_LEVEL=INFO
```

### Paso 4: Crear Frontend Service

```bash
# En Render:
1. New → Web Service
2. Name: aurumai-frontend
3. Root Directory: frontend
4. Environment: Docker
5. Plan: Free

# Environment Variables:
NEXT_PUBLIC_API_URL=https://aurumai-backend.onrender.com
NODE_ENV=production
```

### Paso 5: Ejecutar Migraciones

```bash
# Conectar a la DB de Render localmente
export DATABASE_URL="<EXTERNAL_DATABASE_URL>"

cd backend
source .venv/bin/activate

# Ejecutar Alembic migrations
alembic upgrade head
```

### Paso 6: Health Check

```bash
curl https://aurumai-backend.onrender.com/health

# Expected:
# {"status":"ok","version":"0.1.0"}
```

### Costos Render

```
Free Tier:
- 750h/mes web service
- 1GB PostgreSQL
- Sleep after 15min inactivity
- Ideal para staging

Starter Plan:
- $7/mes web service
- No sleep
- 256MB RAM

Professional Plan:
- $25/mes web service
- 2GB RAM
- Auto-scaling
```

---

## 📊 Comparación de Opciones

| Característica    | Railway     | Cloud Run   | Render      |
| ----------------- | ----------- | ----------- | ----------- |
| **Facilidad**     | ⭐⭐⭐⭐⭐  | ⭐⭐⭐      | ⭐⭐⭐⭐⭐  |
| **Free Tier**     | $5/mes      | 2M req/mes  | 750h/mes    |
| **Escalabilidad** | ⭐⭐⭐⭐    | ⭐⭐⭐⭐⭐  | ⭐⭐⭐      |
| **PostgreSQL**    | ✅ Incluido | Cloud SQL   | ✅ Incluido |
| **Auto-deploy**   | ✅          | ⚠️ Manual   | ✅          |
| **SSL**           | ✅ Auto     | ✅ Auto     | ✅ Auto     |
| **Serverless**    | ❌          | ✅          | ❌          |
| **Costo Staging** | $5-10/mes   | $5-10/mes   | Free        |
| **Costo Prod**    | $30-50/mes  | $30-100/mes | $50-100/mes |

---

## 🎯 Recomendación por Fase

### Fase 1: MVP / Staging

**Recomendado:** Railway o Render (free tier)

```bash
# Railway para mejor experiencia
# Render para 100% free
```

### Fase 2: Beta / Early Production

**Recomendado:** Railway (Hobby plan)

```bash
# $20/mes
# PostgreSQL incluido
# Auto-scaling básico
```

### Fase 3: Production / Scale

**Recomendado:** Google Cloud Run

```bash
# Pay-per-use
# Auto-scaling ilimitado
# Integración con GCP ecosystem
```

---

## 🚀 Quick Start Commands

### Railway

```bash
# Instalar CLI
npm i -g @railway/cli

# Login
railway login

# Link proyecto
railway link

# Deploy
railway up
```

### Cloud Run

```bash
# Build y deploy en un comando
gcloud run deploy aurumai-backend \
  --source backend/ \
  --region us-central1
```

### Render

```bash
# No requiere CLI
# Todo desde Dashboard web
# Push a main → auto-deploy
```

---

## 📝 Checklist Pre-Deploy

Antes de deployar a cualquier plataforma:

- [ ] Docker instalado y funcionando
- [ ] Tests pasando (`pytest tests/`)
- [ ] Builds locales exitosos
- [ ] Secrets generados (SECRET_KEY, passwords)
- [ ] Variables de entorno documentadas
- [ ] Alembic migrations preparadas
- [ ] CORS configurado con dominio real
- [ ] Health endpoints funcionando

---

## 🔗 Referencias

- **Railway:** https://railway.app/docs
- **Cloud Run:** https://cloud.google.com/run/docs
- **Render:** https://render.com/docs
- **Docker:** https://docs.docker.com/

---

**Última actualización:** 15 Nov 2025  
**Próxima acción:** Instalar Docker → Probar Railway/Render
