---
name: Rehabilitar build_docker en CI
about: Volver a habilitar el job de Docker en el workflow una vez estable
labels: ci, docker, enhancement
assignees: ''
---

# Rehabilitar build_docker en CI

## Contexto

El job `build_docker` en `.github/workflows/ci.yaml` está temporalmente deshabilitado (`if: ${{ false }}`) para desbloquear PRs mientras estabilizamos el build de imágenes.

## Criterios de aceptación

- [ ] El build local de las imágenes (API/EDGE) completa sin errores.
- [ ] Tiempo total de build en CI < 10 minutos.
- [ ] Sin dependencias de red externas no cacheadas en el build (o con caché configurada).

## Pasos sugeridos

1. Revisar/normalizar Dockerfiles (API/EDGE) y contexto de build.
2. Añadir caché de capas (actions/cache o `--cache-from`) y consolidar dependencias.
3. Habilitar nuevamente el job cambiando `if: ${{ false }}` → `if: ${{ true }}` o eliminando la condición.
4. Validar el pipeline en un PR de prueba y monitorear tiempos.

## Notas

- Los tests siguen activos en la CI.
- Una vez estable, considerar matrix (api/edge) y caché de capas.
