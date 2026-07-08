"""Interface commune à tous les fournisseurs de capteurs."""

from __future__ import annotations

import abc

from ..model import Snapshot


class SensorProvider(abc.ABC):
    """Un fournisseur sait dire s'il est disponible et produire un Snapshot."""

    #: nom court identifiant la source (affiché dans l'UI).
    name: str = "base"

    @abc.abstractmethod
    def available(self) -> bool:
        """True si ce fournisseur peut fonctionner sur la machine courante."""

    @abc.abstractmethod
    def read(self) -> Snapshot:
        """Retourne un instantané des températures."""
