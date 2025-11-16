# 🎬 Guía de Demo Comercial AurumAI

## 📋 Preparación (5 minutos antes)

### 1. Levantar la plataforma

```bash
docker compose up --build
```

Espera ~2 minutos hasta que veas:

```
✅ Database initialized at aurumai.db
🚀 Edge Simulator starting...
🏭 AurumAI IoT Simulator Starting
```

### 2. Verificar que todo funciona

Abre en el navegador:

- [http://localhost:3000](http://localhost:3000) - Dashboard debe mostrar 3 máquinas
- [http://localhost:8000/docs](http://localhost:8000/docs) - API docs deben cargar

## 🎤 Script de Presentación (10-15 min)

### Intro (1 min)

> "AurumAI es una plataforma industrial IoT que combina mantenimiento predictivo con monitoreo ESG en tiempo real.
>
> Lo que van a ver NO es un PowerPoint. Es un sistema funcionando, con datos reales simulados, machine learning y cálculos de emisiones."

### Pantalla 1: Overview (2 min)

**Mostrar**: [http://localhost:3000](http://localhost:3000)

> "Aquí vemos 3 activos industriales en operación:
>
> - **TRUCK-21**: Camión de acarreo en mina de cobre
> - **MILL-3**: Molino en planta de procesamiento de carbón
> - **BOILER-7**: Caldera industrial en generación de energía
>
> Cada uno está enviando telemetría en tiempo real cada 3 segundos."

**Señalar**:

- Los 3 tarjetas de máquinas
- Estado "operational"
- Tipos diferentes de activos

### Pantalla 2: Mantenimiento Predictivo (5 min)

**Click en**: "Predictive Maintenance"

> "Esta es la vista de mantenimiento predictivo. Seleccionemos el camión TRUCK-21."

**Mostrar**:

- Tarjetas de métricas (Risk, Probability, Next Maintenance)
- Gráfica de tendencia actualizándose

> "Aquí vemos:
>
> - **Riesgo de fallo**: Calculado por ML en base a vibración, temperatura, RPM
> - **Probabilidad de fallo**: Score predictivo
> - **Próximo mantenimiento**: Horas estimadas
>
> La gráfica se actualiza cada 5 segundos con datos nuevos. No es una imagen estática.
>
> Si esperamos unos minutos, veremos cómo el sistema detecta deriva y anomalías."

**Cambiar máquina**:

- Seleccionar MILL-3
- Mostrar que cada máquina tiene su perfil de riesgo

> "El MILL-3 tiene un perfil diferente porque es un molino, no un camión. El modelo ajusta según el tipo de activo."

### Pantalla 3: ESG / Carbono (4 min)

**Click en**: "ESG / Carbon"

> "Ahora pasamos a la vertical ESG. Los mismos datos que usamos para predictivo, también calculan huella de carbono en tiempo real."

**Mostrar**:

- CO₂eq instantáneo
- CO₂eq acumulado
- Consumo de combustible
- Consumo eléctrico

> "Aquí vemos:
>
> - **CO₂eq instantáneo**: Emisiones actuales en kg
> - **CO₂eq acumulado**: Total desde que arrancó
> - **Fuel rate**: Consumo de combustible
> - **Power**: Consumo eléctrico
>
> Usamos factores IPCC estándar:
>
> - Diesel: 2.68 kg CO₂/litro
> - Electricidad LATAM: 0.45 kg CO₂/kWh
>
> El scope se clasifica automáticamente (Scope 1 para combustión directa, Scope 2 para electricidad)."

**Cambiar a BOILER-7**:

> "El boiler tiene emisiones mucho más altas porque consume 20-40 litros/hora de combustible. Perfecto para identificar los mayores emisores de una operación."

### Pantalla 4: API (2 min)

**Abrir**: [http://localhost:8000/docs](http://localhost:8000/docs)

> "Todo esto está expuesto por API REST. Cualquier sistema puede integrarse:
>
> - Ingestión de datos IoT
> - Endpoints de predicción
> - Cálculos ESG
> - Métricas de máquinas
>
> Documentación automática con Swagger."

**Mostrar**:

- Endpoints de `/ingest`
- Endpoints de `/predict`
- Endpoints de `/esg`

### Cierre (1 min)

> "Resumen:
>
> - **1 plataforma**, 3 verticales (Predictivo, ESG, Analytics)
> - **Datos en tiempo real** desde edge nodes
> - **ML integrado** para mantenimiento predictivo
> - **ESG nativo**, no un Excel pegado
> - **Arquitectura escalable**: De 3 máquinas a 10,000
>
> Esto es un mockup funcional, pero la arquitectura ya está lista para producción. Solo hay que reemplazar SQLite por PostgreSQL, y los modelos fake por modelos reales.
>
> ¿Preguntas?"

## 🎯 Respuestas a Preguntas Frecuentes

### "¿Los datos son reales?"
>
> "Son simulados pero realistas. Usamos rangos operacionales reales de maquinaria industrial. En producción conectaríamos sensores reales vía MQTT/OPC-UA."

### "¿El ML es real?"
>
> "El mockup usa heurísticas inteligentes que parecen ML real. En producción usaríamos XGBoost/RandomForest entrenados con datos históricos de fallos."

### "¿Qué tan rápido se puede escalar?"
>
> "La arquitectura hexagonal permite:
>
> - Cambiar base de datos sin tocar lógica de negocio
> - Añadir nuevos tipos de sensores sin refactors
> - Escalar horizontalmente con Kubernetes
> - Multi-tenant desde día 1"

### "¿Cuánto cuesta implementar esto en nuestra operación?"
>
> "Depende de:
>
> - Número de activos
> - Conectividad existente
> - Integración con sistemas legacy
> - Pero el software ya está 80% listo. No empezamos de cero."

### "¿Qué diferencia tiene con otros sistemas?"
>
> "3 cosas:
>
> 1. **ESG nativo**: No es un add-on, está en el core
> 2. **Edge-first**: Funciona con conectividad pobre
> 3. **Multi-vertical**: Predictivo + ESG + Energía + Agua en una plataforma"

## 🔥 Trucos para Impresionar

### Mostrar anomalía en vivo

Si tienes tiempo (7-8 minutos), espera a que el simulador entre en fase "failure" y verás:

- Risk score subiendo dramáticamente
- Gráfica con picos rojos
- Métricas de temperatura/vibración anormales

### Mostrar código fuente

Si la audiencia es técnica, abre:

- `backend/domain/entities/` - Entidades del dominio
- `backend/services/ml_engine.py` - Lógica ML
- `iot-sim/anomalies.py` - Simulación de anomalías

### Mostrar logs en vivo

Deja una terminal visible con:

```bash
docker compose logs -f iot-sim
```

Verás telemetría fluyendo en tiempo real.

## ✅ Checklist Pre-Demo

- [ ] Docker está corriendo
- [ ] Puertos 3000, 8000, 9000 libres
- [ ] `docker compose up` ejecutado y estable
- [ ] Dashboard carga correctamente
- [ ] Has probado la demo una vez antes
- [ ] Pantalla configurada (resolución, brillo)
- [ ] Internet no necesario (todo es local)

---

**¡Buena suerte con la demo!** 🚀
