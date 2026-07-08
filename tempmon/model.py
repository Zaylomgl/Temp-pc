"""Modèle de données pour les relevés de température.

Ce module ne dépend d'aucun capteur : il décrit *ce qui* est mesuré et
comment on qualifie une valeur (normal / attention / critique). Les
fournisseurs (`sensors/`) produisent ces objets, le serveur et la CLI les
consomment.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Status(str, Enum):
    """Statut d'un relevé selon les seuils de sa catégorie."""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class Reading:
    """Un relevé unitaire de température.

    label     : nom lisible du capteur (ex. "Core 0").
    celsius   : valeur mesurée en °C (None si indisponible).
    warning   : seuil d'attention en °C.
    critical  : seuil critique en °C.
    high      : température max relevée par le matériel (optionnel).
    """

    label: str
    celsius: float | None
    warning: float | None = None
    critical: float | None = None
    high: float | None = None

    @property
    def status(self) -> Status:
        if self.celsius is None:
            return Status.UNKNOWN
        if self.critical is not None and self.celsius >= self.critical:
            return Status.CRITICAL
        if self.warning is not None and self.celsius >= self.warning:
            return Status.WARNING
        return Status.NORMAL

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "celsius": self.celsius,
            "warning": self.warning,
            "critical": self.critical,
            "high": self.high,
            "status": self.status.value,
        }


@dataclass
class SensorGroup:
    """Regroupe les relevés d'un même composant (CPU, GPU, disque...)."""

    name: str
    kind: str  # cpu | gpu | disk | board | battery | other
    readings: list[Reading] = field(default_factory=list)

    @property
    def hottest(self) -> Reading | None:
        vals = [r for r in self.readings if r.celsius is not None]
        return max(vals, key=lambda r: r.celsius) if vals else None

    @property
    def status(self) -> Status:
        hot = self.hottest
        return hot.status if hot else Status.UNKNOWN

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "status": self.status.value,
            "hottest": self.hottest.to_dict() if self.hottest else None,
            "readings": [r.to_dict() for r in self.readings],
        }


@dataclass
class Snapshot:
    """Instantané complet à un moment donné."""

    groups: list[SensorGroup] = field(default_factory=list)
    source: str = "unknown"
    timestamp: float = field(default_factory=time.time)

    @property
    def overall_status(self) -> Status:
        order = [Status.CRITICAL, Status.WARNING, Status.NORMAL, Status.UNKNOWN]
        present = {g.status for g in self.groups}
        for s in order:
            if s in present:
                return s
        return Status.UNKNOWN

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "timestamp": self.timestamp,
            "overall_status": self.overall_status.value,
            "groups": [g.to_dict() for g in self.groups],
        }


def summarize(snapshot: Snapshot) -> Iterable[str]:
    """Rend un résumé texte ligne par ligne (utilisé par la CLI)."""
    for g in snapshot.groups:
        hot = g.hottest
        if hot and hot.celsius is not None:
            yield f"{g.name:<22} {hot.celsius:6.1f} °C  [{g.status.value}]"
        else:
            yield f"{g.name:<22} {'--':>6}      [{g.status.value}]"
