# 🎨 Frontend Setup - Next.js Dashboard

**Framework**: Next.js 14 + React 18 + TypeScript + Tailwind CSS  
**Puerto**: 3000  
**Estado**: Requiere Node.js

---

## 🚀 Inicio Rápido

### Prerequisito: Instalar Node.js

Node.js no está instalado en el sistema. Tienes **asdf** disponible.

**Opción 1: Instalar con asdf (Recomendado)**

```bash
# Agregar plugin de Node.js
asdf plugin add nodejs

# Instalar Node.js LTS (v20)
asdf install nodejs latest:20

# Configurar como global
asdf global nodejs latest:20

# Verificar
node --version
npm --version
```

**Opción 2: Instalar con Homebrew**

```bash
brew install node@20
```

---

## 🏃 Levantar Frontend

Una vez Node.js esté instalado:

```bash
cd frontend

# Verificar dependencias (ya instaladas)
ls node_modules/.bin/next

# Levantar servidor de desarrollo
npm run dev
```

**URL**: http://localhost:3000

---

## 📄 Páginas Disponibles

El frontend tiene 3 páginas principales:

### 1. Dashboard (/)

**Archivo**: `src/pages/index.tsx`

- Vista general de máquinas
- Métricas en tiempo real
- Estado operacional

### 2. Predictive Analytics (/predictive)

**Archivo**: `src/pages/predictive.tsx`

- Predicciones de fallas
- Risk scores
- Mantenimiento predictivo

### 3. ESG Monitoring (/esg)

**Archivo**: `src/pages/esg.tsx`

- Emisiones CO₂
- Consumo energético
- Métricas ambientales

---

## 🧩 Componentes

**Ubicación**: `src/components/`

- `MachineCard.tsx` - Tarjeta de máquina
- `MetricCard.tsx` - Tarjeta de métrica
- `LineChart.tsx` - Gráfico de líneas

---

## 🔧 Configuración

### next.config.js

Configuración de Next.js

### tailwind.config.js

Configuración de Tailwind CSS

### tsconfig.json

Configuración de TypeScript

---

## 🌐 Integración con Backend

El frontend se conecta al backend en:

```
http://localhost:8000
```

**Endpoints usados**:

- `GET /machines` - Lista de máquinas
- `GET /machines/{id}/metrics` - Métricas de máquina
- `GET /predict/{id}` - Predicciones
- `GET /esg/{id}` - Datos ESG

---

## 📦 Dependencias

```json
{
  "next": "^14.0.4",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.3.3",
  "tailwindcss": "^3.4.0"
}
```

**Estado**: ✅ Ya instaladas (node_modules existe)

---

## 🚦 Scripts Disponibles

```bash
npm run dev      # Desarrollo (puerto 3000)
npm run build    # Build producción
npm start        # Servidor producción
npm run lint     # Linter
```

---

## 🐳 Docker (Alternativa)

Si prefieres usar Docker sin instalar Node.js:

```bash
cd frontend

# Build imagen
docker build -t aurumai-frontend .

# Run container
docker run -p 3000:3000 aurumai-frontend
```

---

## 🔍 Verificación

Después de `npm run dev`, deberías ver:

```
ready - started server on 0.0.0.0:3000
event - compiled client and server successfully
wait  - compiling...
event - compiled successfully
```

Abrir navegador en: **http://localhost:3000**

---

## 🎯 Demo Completo

Para demo completo con IoT + Edge + Backend + Frontend:

```bash
# Terminal 1: Backend
cd backend
python3 -m uvicorn app:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: IoT + Edge Demo
cd iot-sim
python3 run_demo.py

# Terminal 4: Abrir navegador
open http://localhost:3000
```

---

## ⚠️ Troubleshooting

### Error: npm command not found

**Solución**: Instalar Node.js (ver arriba)

### Error: Port 3000 already in use

**Solución**:

```bash
# Matar proceso en puerto 3000
lsof -ti:3000 | xargs kill -9

# O usar otro puerto
npm run dev -- -p 3001
```

### Error: Module not found

**Solución**:

```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Recursos

- Next.js Docs: https://nextjs.org/docs
- React Docs: https://react.dev
- Tailwind CSS: https://tailwindcss.com/docs

---

**Preparado**: 15 de Noviembre, 2025  
**Estado**: Listo para arrancar (requiere Node.js)
