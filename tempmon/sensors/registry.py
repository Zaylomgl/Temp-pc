"""Sélection automatique du meilleur fournisseur disponible.

Ordre de préférence :
    1. hwmon       — capteurs réels du noyau Linux (le plus précis).
    2. psutil      — repli multiplateforme si la lib est installée.
    3. windows_wmi — zones thermiques ACPI, repli spécifique Windows.
    4. simulé      — dernier recours, toujours disponible.
"""

from __future__ import annotations

from .base import SensorProvider
from .hwmon import HwmonProvider
from .psutil_provider import PsutilProvider
from .simulated import SimulatedProvider
from .windows_wmi import WindowsWmiProvider


def build_provider(force: str | None = None) -> SensorProvider:
    """Retourne un fournisseur prêt à l'emploi.

    force : "hwmon" | "psutil" | "windows_wmi" | "simulated" pour imposer une source.
    """
    candidates: dict[str, SensorProvider] = {
        "hwmon": HwmonProvider(),
        "psutil": PsutilProvider(),
        "windows_wmi": WindowsWmiProvider(),
        "simulated": SimulatedProvider(),
    }

    if force is not None:
        if force not in candidates:
            raise ValueError(
                f"Fournisseur inconnu: {force!r} "
                f"(choix: {', '.join(candidates)})"
            )
        return candidates[force]

    for key in ("hwmon", "psutil", "windows_wmi", "simulated"):
        provider = candidates[key]
        if provider.available():
            return provider
    return candidates["simulated"]  # ne devrait jamais arriver
