# 🔧 Frontend Fix - Pasos Finales

## Problema Identificado

El frontend tenía múltiples problemas:

1. **Loop infinito de peticiones** - `AbortController` mal configurado causaba cancelación prematura
2. **App Router vs Pages Router** - Next.js tenía ambos `src/app/` y `src/pages/`, causando conflictos
3. **Toast Component** - Errores de Server/Client components en App Router

## Solución Aplicada

### 1. ✅ Simplificado `pages/index.tsx`

- Eliminado `useCallback`, `useRef`, y lógica compleja de abort
- Implementado fetch simple con flag `cancelled` para cleanup
- Código mucho más directo y sin reintentos automáticos

### 2. ✅ Eliminado directorio `app/`

- Next.js solo usará `pages/` router (más estable y simple)
- Evita conflictos entre App Router y Pages Router
- Compatible con la estructura actual del proyecto

### 3. ✅ Backend Mock Funcionando

- API endpoint `/machines/` retorna 200 OK
- 5 máquinas mock: CNC-001, CNC-002, PRESS-001, WELD-001, PACK-001
- CORS configurado correctamente para localhost:3000

## 🚀 Pasos para Completar el Fix

### Paso 1: Reiniciar el Frontend

**Detén y reinicia la tarea del Frontend:**

1. En el panel de **TERMINAL**, busca la tarea "Frontend"
2. Haz clic en el icono de 🗑️ (trash/papelera) para detenerla
3. Presiona `Cmd+Shift+P` → "Tasks: Run Task" → "Frontend"
4. Espera 10-15 segundos a que compile

### Paso 2: Verificar que Funciona

Abre http://localhost:3000 en tu navegador y deberías ver:

✅ **"AurumAI Platform"** como título
✅ **"Machines Overview (5)"**
✅ **5 tarjetas de máquinas** mostrando:

- CNC-001 (CNC_MILL, Factory-A, operational)
- CNC-002 (CNC_LATHE, Factory-A, operational)
- PRESS-001 (HYDRAULIC_PRESS, Factory-B, operational)
- WELD-001 (WELDING_ROBOT, Factory-A, offline)
- PACK-001 (PACKAGING_LINE, Factory-C, operational)

### Paso 3: Verificar Backend (Opcional)

```bash
curl http://localhost:8000/machines/
```

Debe retornar JSON con 5 máquinas.

## 📊 Estado de los Servicios

| Servicio      | Puerto | Estado              | Comando                                  |
| ------------- | ------ | ------------------- | ---------------------------------------- |
| Backend       | 8000   | ✅ Running          | `cd backend && uvicorn app:app --reload` |
| Frontend      | 3000   | ⚠️ Necesita Restart | `cd frontend && npm run dev`             |
| IoT Simulator | -      | ✅ Running          | `cd iot-sim && python run_demo.py`       |

## 🐛 Troubleshooting

### Si frontend sigue mostrando "Loading machines..."

1. **Limpia el cache:**

   ```bash
   cd frontend && rm -rf .next && cd ..
   ```

2. **Reinicia el servidor de Next.js** (detén y vuelve a ejecutar la tarea)

3. **Abre DevTools del navegador** (Cmd+Option+I):
   - **Console**: Busca errores de JavaScript
   - **Network**: Verifica que la petición a `/machines/` retorne 200 OK

### Si ves error 404

- Verifica que `frontend/src/pages/index.tsx` existe
- Verifica que NO existe `frontend/src/app/` (debe estar eliminado)
- Reinicia Next.js completamente

### Si ves error de CORS

El backend ya tiene CORS configurado, pero puedes verificar:

```bash
curl -H "Origin: http://localhost:3000" http://localhost:8000/machines/ -v
```

Debe incluir headers:

```
access-control-allow-origin: http://localhost:3000
access-control-allow-credentials: true
```

## 📝 Archivos Modificados

### `frontend/src/pages/index.tsx`

```tsx
// Simplificado - sin retry logic, sin AbortController complejo
useEffect(() => {
  let cancelled = false;

  async function fetchMachines() {
    const response = await fetch(`${API_BASE}/machines/`);
    const data = await response.json();

    if (!cancelled) {
      setMachines(data);
      setLoading(false);
    }
  }

  fetchMachines();
  return () => {
    cancelled = true;
  };
}, []);
```

### `backend/api/routers/machines_mock.py`

```python
# 5 máquinas mock con status válidos
MOCK_MACHINES = [
    {"machine_id": "CNC-001", "status": "operational", ...},
    {"machine_id": "CNC-002", "status": "operational", ...},
    {"machine_id": "PRESS-001", "status": "operational", ...},
    {"machine_id": "WELD-001", "status": "offline", ...},  # Cambiado de 'maintenance'
    {"machine_id": "PACK-001", "status": "operational", ...},
]
```

### `frontend/src/components/Toast.tsx`

```tsx
"use client"; // Agregado al inicio

// Resto del código sin cambios
```

## 🎯 Próximos Pasos (Post-Fix)

Una vez que el frontend funcione:

1. **PostgreSQL Setup** - Instalar y configurar base de datos real
2. **Real Machine Router** - Cambiar de `machines_mock` a `machines` router
3. **MQTT Broker** - Configurar Mosquitto para datos en tiempo real
4. **Grafana Dashboards** - Configurar visualizaciones
5. **Deploy a Staging** - Probar en ambiente cloud

## ✅ Checklist de Verificación

- [ ] Backend corriendo en :8000
- [ ] Frontend corriendo en :3000
- [ ] IoT Simulator corriendo
- [ ] `frontend/src/app/` eliminado
- [ ] Frontend reiniciado después de cambios
- [ ] Navegador muestra 5 máquinas
- [ ] No hay errores en console del navegador
- [ ] Backend logs muestran peticiones GET /machines/ con 200 OK

## 📞 Soporte

Si después de seguir estos pasos el frontend aún no funciona:

1. Copia los logs completos del frontend (panel TERMINAL)
2. Copia los errores del navegador (Console en DevTools)
3. Verifica que `curl http://localhost:8000/machines/` funciona

---

**Última actualización**: 16 Nov 2025, 03:30 AM
**Problema raíz**: Conflicto entre App Router (`src/app/`) y Pages Router (`src/pages/`)  
**Solución**: Eliminar `src/app/` y usar solo Pages Router
