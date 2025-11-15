# 🐳 Docker Setup Guide - macOS

**Para:** Completar deployment a staging  
**Requiere:** Docker Desktop instalado  
**Tiempo estimado:** 10-15 minutos

---

## 📋 Prerrequisitos

### Hardware Mínimo

- **CPU:** Apple Silicon (M1/M2/M3) o Intel Core i5+
- **RAM:** 8 GB (recomendado 16 GB)
- **Disk:** 20 GB libres
- **macOS:** 11.0+ (Big Sur o superior)

---

## 🚀 Opción 1: Instalación Docker Desktop (Recomendado)

### Paso 1: Descargar Docker Desktop

```bash
# Ir a la página oficial
open https://www.docker.com/products/docker-desktop

# O descargar directamente:
# Apple Silicon (M1/M2/M3): Docker Desktop for Mac (Apple Silicon)
# Intel: Docker Desktop for Mac (Intel)
```

### Paso 2: Instalar

1. Abrir el archivo `.dmg` descargado
2. Arrastrar Docker.app a Applications
3. Abrir Docker desde Applications
4. Aceptar permisos de sistema
5. Esperar a que Docker engine inicie (icono en menu bar)

### Paso 3: Verificar Instalación

```bash
# Verificar versiones
docker --version
# Expected: Docker version 24.0.0+

docker-compose --version
# Expected: Docker Compose version v2.20.0+

# Test básico
docker run hello-world
# Expected: "Hello from Docker!"
```

### Paso 4: Configurar Recursos

```
Docker Desktop → Settings → Resources

CPU: 4+ cores
Memory: 4-8 GB
Disk: 60 GB

Apply & Restart
```

---

## 🔧 Opción 2: Instalación con Homebrew

```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Docker
brew install --cask docker

# Abrir Docker Desktop
open -a Docker

# Esperar a que inicie (icono en menu bar)

# Verificar
docker --version
docker-compose --version
```

---

## 🎯 Después de la Instalación

### 1. Build Images Production

```bash
cd /Users/estudio/Projects/GitHub/MOCKUPs/aurumai-mockup

# Build todas las imágenes
docker-compose -f docker-compose.prod.yml build

# Tiempo estimado: 5-10 minutos
# Resultado esperado:
# - aurumai-backend: ~180-200 MB
# - aurumai-frontend: ~130-150 MB
```

### 2. Deploy a Staging Local

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Verificar servicios
docker-compose -f docker-compose.prod.yml ps

# Expected output:
# NAME                STATUS    PORTS
# aurumai-backend     running   0.0.0.0:8000->8000/tcp
# aurumai-frontend    running   0.0.0.0:3000->3000/tcp
# postgres            running   5432/tcp
# timescaledb         running   5433/tcp
# mqtt                running   1883/tcp
```

### 3. Health Checks

```bash
# Backend
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}

# Frontend
curl http://localhost:3000
# Expected: HTML de Next.js

# Metrics
curl http://localhost:8000/metrics
# Expected: Prometheus metrics
```

### 4. Ver Logs

```bash
# Todos los servicios
docker-compose -f docker-compose.prod.yml logs -f

# Solo backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Solo frontend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

---

## 🛠️ Troubleshooting

### Error: "Docker daemon is not running"

```bash
# Solución 1: Abrir Docker Desktop
open -a Docker

# Esperar 30-60 segundos a que inicie

# Solución 2: Restart Docker
# Docker Desktop → Restart
```

### Error: "Cannot connect to Docker daemon"

```bash
# Verificar que Docker está corriendo
docker info

# Si falla, reiniciar Docker Desktop
# Docker Desktop → Quit
# Reabrir Docker Desktop
```

### Error: "Port already in use"

```bash
# Ver qué proceso usa el puerto
lsof -i :8000
lsof -i :3000

# Matar proceso si es necesario
kill -9 <PID>

# O cambiar puerto en docker-compose.prod.yml
```

### Error: "No space left on device"

```bash
# Limpiar imágenes no usadas
docker system prune -a

# Liberar espacio
docker volume prune
docker network prune

# Aumentar disk size
# Docker Desktop → Settings → Resources → Disk image size
```

---

## 📚 Comandos Útiles

### Gestión de Containers

```bash
# Listar containers
docker ps -a

# Parar todos
docker-compose -f docker-compose.prod.yml down

# Parar y eliminar volumes
docker-compose -f docker-compose.prod.yml down -v

# Restart un servicio
docker-compose -f docker-compose.prod.yml restart backend

# Rebuild y restart
docker-compose -f docker-compose.prod.yml up -d --build backend
```

### Gestión de Imágenes

```bash
# Listar imágenes
docker images

# Eliminar imagen
docker rmi <image-id>

# Eliminar todas las no usadas
docker image prune -a

# Ver tamaño
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### Logs y Debug

```bash
# Logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Logs de últimos 5 minutos
docker-compose -f docker-compose.prod.yml logs --since 5m

# Entrar a container
docker exec -it <container-name> /bin/bash

# Ver stats
docker stats
```

---

## 🚀 Deploy Alternativo (Sin Docker Local)

Si no puedes instalar Docker, puedes deployar directamente a cloud:

### Opción A: GitHub Actions + Cloud Run

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Google Cloud Run
        run: |
          gcloud builds submit --tag gcr.io/PROJECT/backend
          gcloud run deploy backend --image gcr.io/PROJECT/backend
```

### Opción B: Railway.app (Sin Config)

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Opción C: Render.com (Web UI)

1. Conectar GitHub repo
2. Select service: Docker
3. Seleccionar Dockerfile
4. Deploy automático

---

## ✅ Checklist Post-Instalación

- [ ] Docker Desktop instalado
- [ ] Docker version >= 24.0
- [ ] docker-compose version >= 2.20
- [ ] Test: `docker run hello-world` exitoso
- [ ] Recursos configurados (4+ CPU, 8+ GB RAM)
- [ ] Images built: `docker images | grep aurumai`
- [ ] Containers running: `docker ps`
- [ ] Health checks: curl endpoints
- [ ] Logs visibles: `docker-compose logs`

---

## 📖 Recursos

- **Docs oficiales:** https://docs.docker.com/desktop/install/mac-install/
- **Troubleshooting:** https://docs.docker.com/desktop/troubleshoot/overview/
- **Best practices:** https://docs.docker.com/develop/dev-best-practices/

---

**Última actualización:** 15 Nov 2025, 23:45  
**Próxima acción:** Instalar Docker Desktop y ejecutar build
