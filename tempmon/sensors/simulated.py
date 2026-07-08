"""Fournisseur simulé : génère des températures réalistes.

Sert de repli quand aucun capteur réel n'est disponible (conteneurs, CI,
machines virtuelles) et permet de faire une démonstration du logiciel. Les
valeurs oscillent doucement autour d'une base par composant, avec un peu de
bruit, pour donner un rendu vivant dans le tableau de bord.
"""

from __future__ import annotations

import math
import random
import time

from ..config import thresholds_for
from ..model import Reading, SensorGroup, Snapshot
from .base import SensorProvider

# (nom, kind, [(label, base °C, amplitude), ...])
_LAYOUT = [
    ("CPU (coretemp)", "cpu", [
        ("Package", 48, 14),
        ("Core 0", 46, 16),
        ("Core 1", 47, 15),
        ("Core 2", 45, 17),
        ("Core 3", 46, 16),
    ]),
    ("GPU (amdgpu)", "gpu", [
        ("edge", 52, 18),
        ("junction", 58, 20),
        ("mem", 54, 12),
    ]),
    ("NVMe SSD", "disk", [
        ("Composite", 40, 8),
    ]),
    ("Carte mère", "board", [
        ("acpitz", 38, 6),
    ]),
]


class SimulatedProvider(SensorProvider):
    name = "simulated"

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self._t0 = time.time()

    def available(self) -> bool:
        return True  # toujours disponible : c'est le dernier recours

    def _value(self, base: float, amp: float, phase: float) -> float:
        elapsed = time.time() - self._t0
        wave = math.sin(elapsed / 12.0 + phase) * (amp / 2.0)
        noise = self._rng.uniform(-1.5, 1.5)
        return round(base + amp / 2.0 + wave + noise, 1)

    def read(self) -> Snapshot:
        groups: list[SensorGroup] = []
        for gi, (name, kind, sensors) in enumerate(_LAYOUT):
            warn, crit = thresholds_for(kind)
            readings = []
            for si, (label, base, amp) in enumerate(sensors):
                readings.append(
                    Reading(
                        label=label,
                        celsius=self._value(base, amp, phase=gi + si * 0.7),
                        warning=warn,
                        critical=crit,
                        high=crit,
                    )
                )
            groups.append(SensorGroup(name=name, kind=kind, readings=readings))
        return Snapshot(groups=groups, source=self.name)
