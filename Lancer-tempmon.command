#!/bin/bash
# ===  tempmon  -  double-cliquez sur ce fichier (macOS) pour lancer  ===
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    python3 launcher.py
else
    echo "Python 3 n'est pas installe."
    echo "Installez-le depuis https://www.python.org/downloads/ puis relancez."
    read -r -p "Appuyez sur Entree pour fermer..."
fi
