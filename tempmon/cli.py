"""Interface en ligne de commande de tempmon."""

from __future__ import annotations

import argparse
import sys
import time

from .config import DEFAULT_HOST, DEFAULT_INTERVAL, DEFAULT_PORT
from .model import Status, summarize
from .sensors import build_provider

# Couleurs ANSI par statut (désactivables si sortie non-TTY).
_COLORS = {
    Status.NORMAL: "\033[32m",
    Status.WARNING: "\033[33m",
    Status.CRITICAL: "\033[31m",
    Status.UNKNOWN: "\033[90m",
}
_RESET = "\033[0m"


def _print_snapshot(snapshot, use_color: bool) -> None:
    for group in snapshot.groups:
        color = _COLORS[group.status] if use_color else ""
        reset = _RESET if use_color else ""
        line = next(iter(summarize_group(group)), "")
        print(f"{color}{line}{reset}")


def summarize_group(group):
    hot = group.hottest
    if hot and hot.celsius is not None:
        yield f"{group.name:<24} {hot.celsius:6.1f} °C  [{group.status.value}]"
    else:
        yield f"{group.name:<24} {'--':>6}      [{group.status.value}]"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tempmon",
        description="Affiche les températures des composants (CPU, GPU, disques...).",
    )
    p.add_argument("--once", action="store_true",
                   help="Afficher un seul relevé puis quitter.")
    p.add_argument("--watch", action="store_true",
                   help="Rafraîchir en continu dans le terminal.")
    p.add_argument("--serve", action="store_true",
                   help="Lancer le tableau de bord web.")
    p.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                   help=f"Intervalle en secondes (défaut: {DEFAULT_INTERVAL}).")
    p.add_argument("--host", default=DEFAULT_HOST,
                   help=f"Hôte du serveur (défaut: {DEFAULT_HOST}).")
    p.add_argument("--port", type=int, default=DEFAULT_PORT,
                   help=f"Port du serveur (défaut: {DEFAULT_PORT}).")
    p.add_argument("--source", choices=["hwmon", "psutil", "simulated"],
                   help="Forcer une source de capteurs.")
    p.add_argument("--no-color", action="store_true",
                   help="Désactiver les couleurs.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    use_color = not args.no_color and sys.stdout.isatty()

    if args.serve:
        from .server import serve
        serve(args.host, args.port, args.source)
        return 0

    provider = build_provider(args.source)

    if args.watch:
        try:
            while True:
                snapshot = provider.read()
                print("\033[2J\033[H", end="")  # efface l'écran
                print(f"tempmon — source: {provider.name} — "
                      f"état global: {snapshot.overall_status.value}\n")
                _print_snapshot(snapshot, use_color)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            return 0

    # Défaut / --once : un seul relevé.
    snapshot = provider.read()
    print(f"Source: {provider.name} — état global: {snapshot.overall_status.value}\n")
    _print_snapshot(snapshot, use_color)
    return 0
