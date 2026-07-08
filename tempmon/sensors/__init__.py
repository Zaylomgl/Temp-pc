"""Fournisseurs de capteurs de température."""

from .base import SensorProvider
from .registry import build_provider

__all__ = ["SensorProvider", "build_provider"]
