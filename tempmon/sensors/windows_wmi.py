"""Lecteur de capteurs Windows via WMI (zones thermiques ACPI).

Windows n'expose pas d'équivalent direct à /sys/class/hwmon, et
`psutil.sensors_temperatures()` n'est disponible que sur Linux/FreeBSD.
Le repli le plus proche sans dépendance lourde est la classe WMI standard
`MSAcpi_ThermalZoneTemperature` (namespace `root\\WMI`), qui expose les
zones thermiques ACPI de la carte mère en dixièmes de Kelvin.

Limites connues : selon le fabricant, seule une poignée de zones (voire
aucune) sont exposées ou mises à jour par le firmware, et l'accès requiert
généralement des droits administrateur. Sur ces machines, tempmon retombe
alors sur la source simulée.
"""

from __future__ import annotations

from ..config import thresholds_for
from ..model import Reading, SensorGroup, Snapshot
from .base import SensorProvider

try:  # import paresseux : wmi/pywin32 ne sont utiles que sur Windows.
    import wmi  # type: ignore
except Exception:  # pragma: no cover - dépend de l'environnement
    wmi = None


def _kelvin_tenths_to_celsius(value: float) -> float:
    return (value / 10.0) - 273.15


def _classify(name: str) -> str:
    lower = name.lower()
    if "cpu" in lower:
        return "cpu"
    if "gpu" in lower:
        return "gpu"
    return "board"


class WindowsWmiProvider(SensorProvider):
    name = "windows_wmi"

    def __init__(self) -> None:
        self._connection = None

    def _connect(self):
        if self._connection is None and wmi is not None:
            self._connection = wmi.WMI(namespace="root\\WMI")
        return self._connection

    def available(self) -> bool:
        if wmi is None:
            return False
        try:
            conn = self._connect()
            zones = conn.MSAcpi_ThermalZoneTemperature()
            return bool(zones)
        except Exception:
            return False

    def read(self) -> Snapshot:
        groups: list[SensorGroup] = []
        conn = self._connect()
        zones = conn.MSAcpi_ThermalZoneTemperature()
        kind = "board"
        default_warn, default_crit = thresholds_for(kind)
        readings: list[Reading] = []
        for i, zone in enumerate(zones):
            label = getattr(zone, "InstanceName", None) or f"TZ{i}"
            celsius = _kelvin_tenths_to_celsius(zone.CurrentTemperature)
            readings.append(
                Reading(
                    label=label,
                    celsius=celsius,
                    warning=default_warn,
                    critical=default_crit,
                )
            )
        if readings:
            groups.append(SensorGroup(name="ACPI", kind=kind, readings=readings))
        return Snapshot(groups=groups, source=self.name)
