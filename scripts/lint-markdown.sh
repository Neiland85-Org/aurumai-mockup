#!/bin/bash
# Script para ejecutar MarkdownLint en el proyecto
# Uso: ./scripts/lint-markdown.sh [archivo-opcional]

set -e

echo "🔍 Ejecutando MarkdownLint..."

# Verificar si markdownlint-cli está instalado
if ! command -v markdownlint &> /dev/null; then
    echo "❌ MarkdownLint no está instalado."
    echo "📦 Instalando globalmente..."
    npm install -g markdownlint-cli
fi

# Configuración
CONFIG_FILE=".markdownlint.json"
MARKDOWN_FILES="**/*.md"

# Si se proporciona un archivo específico, usarlo
if [ $# -eq 1 ]; then
    MARKDOWN_FILES="$1"
fi

echo "📁 Analizando archivos: $MARKDOWN_FILES"
echo "⚙️  Configuración: $CONFIG_FILE"
echo ""

# Ejecutar MarkdownLint
markdownlint "$MARKDOWN_FILES" --config "$CONFIG_FILE"

echo ""
echo "✅ MarkdownLint completado exitosamente"

# Mostrar ayuda para corrección automática
echo ""
echo "💡 Para corregir automáticamente cuando sea posible:"
echo "   markdownlint --fix \"$MARKDOWN_FILES\" --config \"$CONFIG_FILE\""