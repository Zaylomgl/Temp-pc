"""Seuils par défaut et réglages.

Les seuils dépendent de la catégorie de composant : un disque à 55 °C est
"chaud" alors qu'un CPU à 55 °C est parfaitement normal. Ces valeurs servent
uniquement de repli quand le matériel n'expose pas ses propres seuils.
"""

from __future__ import annotations

# (warning, critical) en °C, par type de composant.
DEFAULT_THRESHOLDS: dict[str, tuple[float, float]] = {
    "cpu": (80.0, 95.0),
    "gpu": (83.0, 95.0),
    "disk": (55.0, 65.0),
    "board": (70.0, 85.0),
    "battery": (50.0, 60.0),
    "other": (75.0, 90.0),
}

# Réglages serveur / rafraîchissement.
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
DEFAULT_INTERVAL = 2.0  # secondes entre deux relevés (CLI et front)


def thresholds_for(kind: str) -> tuple[float, float]:
    return DEFAULT_THRESHOLDS.get(kind, DEFAULT_THRESHOLDS["other"])
