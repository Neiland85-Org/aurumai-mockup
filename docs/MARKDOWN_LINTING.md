# Markdown Linting

Este proyecto utiliza [MarkdownLint](https://github.com/DavidAnson/markdownlint)
para mantener la consistencia y calidad de la documentación.

## 🚀 Configuración

### Extensión VSCode (Recomendada)

1. **Instala la extensión**: `DavidAnson.vscode-markdownlint`
2. **Configuración automática**: La extensión detectará automáticamente `.markdownlint.json`
3. **Auto-fix**: `Ctrl+Shift+P` → "Fix all auto-fixable problems"

### Configuración en VSCode

La configuración está incluida en `.vscode/settings.json`:

```json
"[markdown]": {
  "editor.defaultFormatter": "DavidAnson.vscode-markdownlint",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.markdownlint": "explicit"
  }
}
```

## 📋 Reglas Configuradas

| Regla | Estado | Descripción |
|-------|--------|-------------|
| MD013 | ✅ 100 chars | Longitud máxima de línea |
| MD034 | ❌ Deshabilitado | Permite URLs sin formato |
| MD036 | ❌ Deshabilitado | Permite énfasis en lugar de headings |
| MD040 | ❌ Deshabilitado | No requiere lenguaje en code blocks |
| MD041 | ❌ Deshabilitado | No requiere heading al inicio |

**Ver configuración completa**: `.markdownlint.json`

## 🛠️ Uso Local

### Opción 1: Script Automático

```bash
# Verificar todos los archivos .md
./scripts/lint-markdown.sh

# Verificar archivo específico
./scripts/lint-markdown.sh README.md

# Auto-corregir cuando sea posible
markdownlint --fix "**/*.md" --config .markdownlint.json
```

### Opción 2: Línea de Comandos Directa

```bash
# Instalar si no está disponible
npm install -g markdownlint-cli

# Verificar archivos
markdownlint "**/*.md" --config .markdownlint.json

# Auto-corregir
markdownlint --fix "**/*.md" --config .markdownlint.json
```

## 🔄 CI/CD Integration

MarkdownLint se ejecuta automáticamente en GitHub Actions:

```yaml
lint-docs:
  name: 📝 Lint Documentation
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Install MarkdownLint
      run: npm install -g markdownlint-cli
    - name: Run MarkdownLint
      run: markdownlint "**/*.md" --config .markdownlint.json
```

## 📚 Reglas Comunes

### Errores Frecuentes

1. **MD013 - Line length**: Líneas muy largas (>100 caracteres)
   - **Solución**: Dividir en múltiples líneas o reformatear

2. **MD040 - Fenced code language**: Code blocks sin lenguaje especificado
   - **Nota**: Esta regla está deshabilitada en este proyecto

3. **MD034 - Bare URL**: URLs sin formato Markdown
   - **Nota**: Esta regla está deshabilitada para permitir URLs directas

### Corrección Automática

Muchas reglas se pueden corregir automáticamente:

```bash
# Corregir todo lo posible
markdownlint --fix "**/*.md" --config .markdownlint.json

# Corregir archivo específico
markdownlint --fix README.md --config .markdownlint.json
```

## 🎯 Mejores Prácticas

### Para Contribuidores

1. **Antes de commit**: Ejecuta `./scripts/lint-markdown.sh`
2. **En VSCode**: Los errores se muestran automáticamente
3. **Auto-fix**: Usa `Ctrl+Shift+P` → "Fix all auto-fixable problems"

### Para Mantenedores

1. **Actualizar configuración**: Modifica `.markdownlint.json`
2. **Testing**: Prueba cambios con `./scripts/lint-markdown.sh`
3. **CI/CD**: Los cambios se validan automáticamente

## 📞 Solución de Problemas

### "markdownlint: command not found"

```bash
# Instalar globalmente
npm install -g markdownlint-cli

# Verificar instalación
markdownlint --version
```

### Errores de configuración

```bash
# Validar JSON
cat .markdownlint.json | jq .

# Probar configuración
markdownlint --help config
```

### Extensión VSCode no funciona

1. **Recargar VSCode**: `Ctrl+Shift+P` → "Developer: Reload Window"
2. **Verificar instalación**: Extensiones → Buscar "markdownlint"
3. **Configuración**: Asegurarse que `.vscode/settings.json` existe

## 📈 Métricas

- **Archivos analizados**: Todos los `.md` en el proyecto
- **Límite de línea**: 100 caracteres
- **Estilo**: Consistente (ATX o Setext)
- **Code blocks**: Lenguaje opcional

---

**Última actualización**: $(date)
**Configuración**: `.markdownlint.json`
**Script**: `scripts/lint-markdown.sh`
