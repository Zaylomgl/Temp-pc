"""Serveur HTTP minimal (stdlib) : API JSON + tableau de bord statique.

Routes :
    GET /                -> tableau de bord (web/index.html)
    GET /style.css       -> feuille de style
    GET /app.js          -> logique front
    GET /api/snapshot    -> instantané JSON des températures
"""

from __future__ import annotations

import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .sensors import build_provider


def _web_dir() -> str:
    # Quand l'appli est packagée avec PyInstaller (.exe), les fichiers
    # statiques sont extraits dans sys._MEIPASS/tempmon/web.
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, "tempmon", "web")
    return os.path.join(os.path.dirname(__file__), "web")


WEB_DIR = _web_dir()

_STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
}


def make_handler(provider):
    class Handler(BaseHTTPRequestHandler):
        server_version = "tempmon/1.0"

        def log_message(self, fmt, *args):  # silence par défaut
            pass

        def _send(self, code, body: bytes, content_type: str):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]

            if path == "/api/snapshot":
                snap = provider.read()
                body = json.dumps(snap.to_dict()).encode("utf-8")
                return self._send(200, body, "application/json; charset=utf-8")

            if path in _STATIC:
                filename, ctype = _STATIC[path]
                full = os.path.join(WEB_DIR, filename)
                try:
                    with open(full, "rb") as fh:
                        return self._send(200, fh.read(), ctype)
                except OSError:
                    return self._send(404, b"Not found", "text/plain")

            self._send(404, b"Not found", "text/plain")

        do_HEAD = do_GET

    return Handler


def serve(host: str, port: int, force_provider: str | None = None,
          open_browser: bool = False) -> None:
    provider = build_provider(force_provider)
    handler = make_handler(provider)
    httpd = ThreadingHTTPServer((host, port), handler)
    # Sur "0.0.0.0" on ouvre localhost côté navigateur.
    display_host = "localhost" if host in ("0.0.0.0", "") else host
    url = f"http://{display_host}:{port}"
    print(f"tempmon : source de capteurs = {provider.name}")
    print(f"Tableau de bord : {url}")
    print("Ferme cette fenetre (ou Ctrl+C) pour arreter.")

    if open_browser:
        # Laisse le serveur démarrer avant d'ouvrir le navigateur.
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArret.")
    finally:
        httpd.server_close()
