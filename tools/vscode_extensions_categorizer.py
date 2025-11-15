#!/usr/bin/env python3
"""
Categoriza IDs de extensiones de VS Code por categorías heurísticas.
Uso:
  cat extensions.txt | python tools/vscode_extensions_categorizer.py
"""
import sys
from collections import defaultdict

CATEGORIES = {
    'ai': ['github.copilot', 'github.copilot-chat', 'github.copilot-labs'],
    'python': ['ms-python.python', 'ms-python.vscode-pylance', 'ms-toolsai.jupyter'],
    'format': ['esbenp.prettier-vscode', 'dbaeumer.vscode-eslint', 'ms-python.black-formatter', 'ms-python.isort'],
    'ui': ['miguelsolorio.symbols'],
}

# normaliza a minúsculas para comparar
canon = {k: [s.lower() for s in v] for k, v in CATEGORIES.items()}

by_cat = defaultdict(list)
unknown = []

def categorize(ext_id: str):
    e = ext_id.strip()
    if not e:
        return
    el = e.lower()
    matched = False
    for cat, ids in canon.items():
        for known in ids:
            if el == known:
                by_cat[cat].append(e)
                matched = True
                break
        if matched:
            break
    if not matched:
        unknown.append(e)

if __name__ == '__main__':
    data = sys.stdin.read().splitlines()
    for line in data:
        categorize(line)

    print('=== CATEGORÍAS ===')
    for cat, items in by_cat.items():
        print(f'[{cat}] ({len(items)})')
        for it in sorted(items):
            print(f'  - {it}')
        print()

    print('[unknown] ({})'.format(len(unknown)))
    for it in sorted(unknown):
        print(f'  - {it}')

    # Sugerencias rápidas
    suggestions = []
    if len(by_cat.get('ai', [])) > 1:
        suggestions.append('IA: Mantén solo una variante (p. ej., GitHub.copilot).')
    if 'esbenp.prettier-vscode' in by_cat.get('format', []) and 'dbaeumer.vscode-eslint' in by_cat.get('format', []):
        suggestions.append('Format/Lint: Evita solapamientos entre Prettier y ESLint en formateo automático.')
    if 'miguelsolorio.symbols' in by_cat.get('ui', []):
        suggestions.append('UI: Considera desactivar temporalmente miguelsolorio.symbols (reportado en logs).')

    if suggestions:
        print('\n=== SUGERENCIAS ===')
        for s in suggestions:
            print(f'- {s}')
