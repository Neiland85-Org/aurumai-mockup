# 🎨 Levantar Frontend - Paso a Paso

## Situación Actual

- ✅ Frontend Next.js existe y está configurado
- ✅ Dependencias (node_modules) ya instaladas
- ❌ Node.js no está disponible en PATH

---

## Solución Rápida

### Instalar Node.js con asdf

```bash
# 1. Agregar plugin
asdf plugin add nodejs

# 2. Instalar Node.js 20 (LTS)
asdf install nodejs latest:20

# 3. Configurar globalmente
asdf global nodejs latest:20

# 4. Recargar shell
source ~/.zshrc

# 5. Verificar
node --version
npm --version
```

---

## Levantar Frontend

```bash
cd frontend
npm run dev
```

**URL**: http://localhost:3000

---

## Páginas

- `/` - Dashboard principal
- `/predictive` - Análisis predictivo
- `/esg` - Monitoreo ESG

---

**Tiempo estimado**: 5 minutos

Ver **FRONTEND_SETUP.md** para más detalles.
