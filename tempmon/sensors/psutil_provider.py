"""Fournisseur multiplateforme basé sur psutil (optionnel).

psutil n'est pas une dépendance obligatoire : s'il n'est pas installé, ce
fournisseur se déclare simplement indisponible et le registre passe au
suivant. Utile surtout hors Linux ou quand hwmon n'est pas monté.
"""

from __future__ import annotations

from ..config import thresholds_for
from ..model import Reading, SensorGroup, Snapshot
from .base import SensorProvider

try:  # import paresseux : psutil est facultatif
    import psutil  # type: ignore
except Exception:  # pragma: no cover - dépend de l'environnement
    psutil = None


_NAME_KIND = {
    "coretemp": "cpu",
    "k10temp": "cpu",
    "cpu": "cpu",
    "acpitz": "board",
    "nvme": "disk",
    "amdgpu": "gpu",
}


def _classify(name: str) -> str:
    lower = name.lower()
    for key, kind in _NAME_KIND.items():
        if key in lower:
            return kind
    return "other"


class PsutilProvider(SensorProvider):
    name = "psutil"

    def available(self) -> bool:
        if psutil is None or not hasattr(psutil, "sensors_temperatures"):
            return False
        try:
            return bool(psutil.sensors_temperatures())
        except Exception:
            return False

    def read(self) -> Snapshot:
        groups: list[SensorGroup] = []
        data = psutil.sensors_temperatures()  # {chip: [shwtemp, ...]}
        for chip, entries in data.items():
            kind = _classify(chip)
            default_warn, default_crit = thresholds_for(kind)
            readings = []
            for i, e in enumerate(entries):
                label = getattr(e, "label", "") or f"{chip}{i}"
                readings.append(
                    Reading(
                        label=label,
                        celsius=getattr(e, "current", None),
                        warning=getattr(e, "high", None) or default_warn,
                        critical=getattr(e, "critical", None) or default_crit,
                        high=getattr(e, "high", None),
                    )
                )
            if readings:
                groups.append(SensorGroup(name=chip, kind=kind, readings=readings))
        return Snapshot(groups=groups, source=self.name)
