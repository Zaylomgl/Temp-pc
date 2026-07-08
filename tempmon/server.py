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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .sensors import build_provider

WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

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


def serve(host: str, port: int, force_provider: str | None = None) -> None:
    provider = build_provider(force_provider)
    handler = make_handler(provider)
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"tempmon : source de capteurs = {provider.name}")
    print(f"Tableau de bord : http://{host}:{port}")
    print("Ctrl+C pour arrêter.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt.")
    finally:
        httpd.server_close()
