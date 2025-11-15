# Guía rápida: estabilizar VS Code (host de extensiones)

Esta guía te ayuda a identificar extensiones problemáticas y a estabilizar el host de extensiones cuando aparecen mensajes como "unresponsive", abortos de `onWillSave` y errores en snippets.

## 1) Mitigaciones inmediatas (ya aplicadas en este workspace)

- Desactivado `editor.formatOnSave` y `organizeImports` en guardado a nivel de workspace.
- Desactivadas actualizaciones automáticas de extensiones (`extensions.autoUpdate: false`).

Puedes revertir estas mitigaciones cuando el entorno esté estable.

## 2) Arregla el snippet corrupto

- Paleta (⇧⌘P) → "Preferences: Configure User Snippets" → `settings.json`.
- Si no lo usas, déjalo como `{}`. Si lo usas, asegúrate de que el contenido sea un objeto válido con definiciones de snippet.

## 3) Aislar la extensión problemática

- Paleta → "Developer: Start Extension Bisect" y sigue los pasos. Esto deshabilita/rehabilita subconjuntos de extensiones hasta aislar la responsable.
- Paleta → "Developer: Show Running Extensions" y ordena por `Activation time` y `CPU %`.
- Paleta → "Developer: Open Process Explorer" para ver consumo de CPU del host.
- Paleta → "Developer: Startup Performance" para detectar picos de carga.
- Paleta → "Developer: Generate CPU Profile" mientras guardas un archivo grande para capturar el hotspot.

## 4) Política de extensiones (recomendada)

- IA: mantén solo una variante (p. ej., `GitHub.copilot`). Evita tener Chat + Copilot + Labs a la vez.
- Python: `ms-python.python` y `ms-python.vscode-pylance`.
- Formateo: evita solapamientos; si usas Prettier, desactiva otros formatters del mismo lenguaje.
- UI/Productividad: desinstala las que no uses a diario.
- Evitar temporalmente: `miguelsolorio.symbols` (observamos errores de actualización en logs).

## 5) CLI opcional

- Paleta → "Shell Command: Install 'code' command in PATH" (reinicia terminales).
- Luego:
  - Listar extensiones: `code --list-extensions`
  - Estado del proceso: `code --status`

## 6) Reintroducir funciones gradualmente

- Rehabilita `editor.formatOnSave` y `organizeImports` por lenguaje:

  ```jsonc
  {
    "[python]": { "editor.formatOnSave": true }
  }
  ```

- Reactiva actualizaciones (`extensions.autoUpdate: true`) cuando no haya unresponsive.

## 7) Si reaparecen errores

- Adjunta el listado de extensiones y el CPU profile. Podemos priorizar desactivaciones y preparar una lista final de recomendaciones.

---

Anexo: si usas proxy/SSL estricto, revisa la configuración de red de VS Code para evitar `net::ERR_FAILED` durante actualizaciones.
