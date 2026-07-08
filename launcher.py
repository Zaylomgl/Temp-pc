"""Point d'entrée « double-clic » de tempmon.

Sans argument (cas du .exe lancé au clic), on démarre le tableau de bord web
et on ouvre le navigateur automatiquement. Avec des arguments, on se comporte
comme la CLI normale (`--once`, `--watch`, etc.).

Ce fichier sert aussi de point d'entrée à PyInstaller pour générer tempmon.exe.
"""

import sys

from tempmon.cli import main

if __name__ == "__main__":
    # Aucun argument => mode grand public : dashboard + ouverture navigateur.
    if len(sys.argv) == 1:
        sys.argv += ["--serve", "--open"]
    raise SystemExit(main())
