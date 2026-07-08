#!/bin/bash
# ===  tempmon  -  lanceur Linux  ===
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    exec python3 launcher.py "$@"
else
    echo "Python 3 n'est pas installe. Installez-le via votre gestionnaire de paquets."
    exit 1
fi
