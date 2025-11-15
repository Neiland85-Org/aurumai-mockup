# Fase 2 Optimizada - IoT & Edge Simulators Simplificados

Fecha: 14 de Noviembre, 2025
Objetivo: Reducir tiempo de implementación de 4-6 días a 2-3 días
Reducción: 50% del tiempo sin pérdida de funcionalidad core

📊 Resumen Ejecutivo
Cambios Principales
Aspecto    Original (ROADMAP.md)    Optimizado    Ahorro
Máquinas    3 (TRUCK-21, MILL-3, BOILER-7)    1 (TRUCK-21)    1 día
Protocolo    HTTP + MQTT    Solo HTTP    1 día
Buffer    SQLite persistente    Queue en memoria    0.5 días
Inferencia    ONNX local en edge    Solo backend    1 día
Anomalías    Sistema complejo de inyección    Hardcoded progresivo    0.5 días
Async    AsyncIO completo    Sync simple    0.5 días
TOTAL    4-6 días    2-3 días    ✂️ 50%
📁 Archivos Simplificados Creados
IoT Simulator
Edge Simulator
🚀 Guía de Implementación (2-3 días)
Día 1: IoT Simulator Simplificado
Objetivos
 Clase TruckSimulator con generación de datos
 Rangos normales y de fallo definidos
 Progresión automática: normal → degradación → fallo
 Publicador HTTP simple
Implementación
Testing
Tiempo estimado: 4-6 horas

Día 2: Edge Simulator Mínimo
Objetivos
 Clase FeatureEngine con SMA, derivadas, min/max
 Queue en memoria (Python queue.Queue)
 Cliente HTTP para sync al backend
 Loop principal de procesamiento
Implementación
Testing
Tiempo estimado: 4-6 horas

Día 3: Integración y Testing
Objetivos
 Conectar IoT → Edge → Backend
 Script run_demo.py integrado
 Verificar flujo end-to-end
 Ajustes y debugging
Implementación
Testing End-to-End
Tiempo estimado: 4-8 horas

✅ Funcionalidad Mantenida (Core del Mockup)
Generación de Datos Realistas
✅ Sensores industriales (vibración, temperatura, RPM, CO₂, combustible)
✅ Rangos operacionales normales
✅ Progresión realista hacia fallo
Feature Engineering
✅ Simple Moving Average (SMA)
✅ Derivadas (rate of change)
✅ Min/Max sobre ventana deslizante
✅ Ventana configurable (default: 10 samples)
Integración con Backend
✅ POST /ingest/raw - Telemetría cruda
✅ POST /ingest/features - Features computadas
✅ Formato JSON estándar
✅ Retry logic básico
Simulación de Anomalías
✅ Operación normal (samples 0-600)
✅ Degradación gradual (samples 601-800)
✅ Estado crítico/fallo (samples 801+)
Demostración Arquitectura
✅ Separación IoT / Edge / Backend
✅ Flujo de datos end-to-end
✅ Processing en edge
✅ Sync a backend centralizado
❌ Funcionalidad Removida (No Crítica para Mockup)
MQTT Broker y Publisher
Original: Eclipse Mosquitto broker + paho-mqtt client
Eliminado: Usar solo HTTP REST
Razón: Simplifica deployment, HTTP es suficiente para demo
Ahorro: 1 día (no need broker setup, MQTT config, QoS handling)

Buffer SQLite Persistente
Original: Store-and-forward con SQLite local
Eliminado: Queue en memoria (Python queue.Queue)
Razón: Para demo no necesitamos resiliencia offline
Ahorro: 0.5 días (no DB schema, no persistence logic)

Inferencia ONNX Local
Original: Modelo ML en edge vía ONNX Runtime
Eliminado: Toda inferencia en backend
Razón: Edge solo hace feature engineering
Ahorro: 1 día (no ONNX export, no edge deployment)

Máquinas Adicionales
Original: TRUCK-21, MILL-3, BOILER-7
Eliminado: Solo TRUCK-21
Razón: Un tipo de máquina es suficiente para demo
Ahorro: 1 día (no múltiples configuraciones)

Sistema Complejo de Anomalías
Original: Módulo anomalies.py con inyección dinámica
Eliminado: Progresión hardcoded en generate_sample()
Razón: Patrón progresivo es más predecible para demo
Ahorro: 0.5 días (no logic de detección/inyección)

AsyncIO Completo
Original: async/await en todo el flujo
Eliminado: Código sincrónico simple
Razón: Menor complejidad, threads son suficientes
Ahorro: 0.5 días (no async coordination, simpler debugging)

📈 Impacto en Timeline General
Timeline Original (ROADMAP.md)
Timeline Optimizado
Ahorro total: 2-3 días en Fase 2
Beneficio adicional: Código más simple = menos bugs, más rápido debuggear

🔄 Migración a Versión Completa (Futuro)
Si en el futuro se necesita la versión completa con MQTT, buffer, etc:

Paso 1: Agregar MQTT (1 día)
Paso 2: Agregar Buffer SQLite (0.5 días)
Paso 3: Agregar Inferencia ONNX (1 día)
Paso 4: Agregar Máquinas (0.5 días)
Total para migración: 3 días

🎯 Decisión Final
Usar Versión Simplificada para
Mockup demo inicial
Pruebas de concepto
Validación de arquitectura
Presentaciones a stakeholders
Usar Versión Completa para
MVP en producción
Sites con conectividad pobre
Deployment a escala
Edge computing real
📝 Próximos Pasos
Esta Semana (Día 1-3)
 Implementar generator_simplified.py
 Implementar main_simplified.py
 Crear run_demo.py integrado
 Testing end-to-end con backend
Próxima Semana (Fase 3)
 Frontend Next.js
 Dashboard con visualización de datos
 Gráficos de vibración, temperatura
 Alertas en UI
🔗 Referencias
ROADMAP.md: Plan original completo
generator.py: Implementación original (referencia)
main.py: Implementación original (referencia)
ARCHITECTURE.md: Arquitectura hexagonal del sistema
✅ Versión simplificada lista para implementar

Tiempo total Fase 2: 2-3 días
Ahorro: 50% vs plan original
Funcionalidad core: 100% mantenida
Complejidad: Reducida significativamente

¡Manos a la obra! 🚀

```cpp
// Ejemplo correcto (4 espacios)
    int main() {
        return 0;
    }
```
