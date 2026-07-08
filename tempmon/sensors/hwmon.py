"""Lecteur réel des capteurs Linux via /sys/class/hwmon.

Le noyau expose chaque puce de monitoring sous /sys/class/hwmon/hwmonN/ avec
des fichiers texte :
    name              -> nom de la puce (coretemp, k10temp, nvme, acpitz...)
    tempX_label       -> nom lisible du capteur X (optionnel)
    tempX_input       -> température en milli-°C
    tempX_max         -> seuil "high" en milli-°C (optionnel)
    tempX_crit        -> seuil critique en milli-°C (optionnel)

Ce module lit ces fichiers, sans aucune dépendance externe.
"""

from __future__ import annotations

import glob
import os

from ..config import thresholds_for
from ..model import Reading, SensorGroup, Snapshot
from .base import SensorProvider

HWMON_ROOT = "/sys/class/hwmon"

# Association nom de puce -> catégorie de composant.
_CHIP_KIND = {
    "coretemp": "cpu",
    "k10temp": "cpu",
    "zenpower": "cpu",
    "cpu_thermal": "cpu",
    "amdgpu": "gpu",
    "nouveau": "gpu",
    "nvme": "disk",
    "drivetemp": "disk",
    "acpitz": "board",
    "pch": "board",
    "BAT": "battery",
}


def _classify(chip_name: str) -> str:
    lower = chip_name.lower()
    for key, kind in _CHIP_KIND.items():
        if key.lower() in lower:
            return kind
    return "other"


def _read_text(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read().strip()
    except (OSError, ValueError):
        return None


def _read_milli(path: str) -> float | None:
    raw = _read_text(path)
    if raw is None:
        return None
    try:
        return int(raw) / 1000.0
    except ValueError:
        return None


def _parse_chip(chip_dir: str) -> SensorGroup | None:
    chip_name = _read_text(os.path.join(chip_dir, "name")) or os.path.basename(chip_dir)
    kind = _classify(chip_name)
    default_warn, default_crit = thresholds_for(kind)

    readings: list[Reading] = []
    inputs = sorted(glob.glob(os.path.join(chip_dir, "temp*_input")))
    for input_path in inputs:
        prefix = input_path[: -len("_input")]  # .../tempX
        idx = os.path.basename(prefix)  # tempX
        celsius = _read_milli(input_path)
        if celsius is None:
            continue
        label = _read_text(f"{prefix}_label") or idx
        crit = _read_milli(f"{prefix}_crit")
        high = _read_milli(f"{prefix}_max")
        readings.append(
            Reading(
                label=label,
                celsius=celsius,
                warning=high if high is not None else default_warn,
                critical=crit if crit is not None else default_crit,
                high=high,
            )
        )

    if not readings:
        return None
    return SensorGroup(name=chip_name, kind=kind, readings=readings)


class HwmonProvider(SensorProvider):
    name = "hwmon"

    def available(self) -> bool:
        return os.path.isdir(HWMON_ROOT) and bool(os.listdir(HWMON_ROOT))

    def read(self) -> Snapshot:
        groups: list[SensorGroup] = []
        for chip_dir in sorted(glob.glob(os.path.join(HWMON_ROOT, "hwmon*"))):
            group = _parse_chip(chip_dir)
            if group is not None:
                groups.append(group)
        return Snapshot(groups=groups, source=self.name)
