#!/usr/bin/env python3
"""Inventory service. Reports which Pod served the request."""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
POD_NAME = os.environ.get("POD_NAME") or os.environ.get("HOSTNAME", "local")

ITEMS = {
    "laptop": {"name": "Laptop", "quantity_on_hand": 5},
    "keyboard": {"name": "Keyboard", "quantity_on_hand": 12},
    "headphones": {"name": "Headphones", "quantity_on_hand": 0},
}

ready_lock = threading.Lock()
ready = True


def is_ready():
    with ready_lock:
        return ready


def set_ready(value):
    global ready
    with ready_lock:
        ready = value
    print(f"[{POD_NAME}] readiness set to {value}", flush=True)


class InventoryHandler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        payload = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        try:
            path = self.path.split("?", 1)[0]
            if path == "/health":
                self._send(200, {"status": "ok", "pod": POD_NAME})
                return
            if path == "/ready":
                if is_ready():
                    self._send(200, {"ready": True, "pod": POD_NAME})
                else:
                    self._send(503, {"ready": False, "pod": POD_NAME})
                return
            parts = [part for part in path.split("/") if part]
            if len(parts) == 2 and parts[0] == "items":
                self._item(parts[1])
                return
            self._send(404, {"error": "not_found", "pod": POD_NAME})
        except Exception as exc:
            print(f"[{POD_NAME}] request failed: {exc}", flush=True)
            self._send(500, {"error": "internal_error", "pod": POD_NAME})

    def do_POST(self):
        try:
            path = self.path.split("?", 1)[0]
            if path == "/admin/readiness/fail":
                set_ready(False)
                self._send(200, {"ready": False, "pod": POD_NAME})
                return
            if path == "/admin/readiness/restore":
                set_ready(True)
                self._send(200, {"ready": True, "pod": POD_NAME})
                return
            self._send(404, {"error": "not_found", "pod": POD_NAME})
        except Exception as exc:
            print(f"[{POD_NAME}] request failed: {exc}", flush=True)
            self._send(500, {"error": "internal_error", "pod": POD_NAME})

    def _item(self, item_id):
        item = ITEMS.get(item_id)
        if item is None:
            self._send(404, {"error": "item_not_found", "item_id": item_id, "pod": POD_NAME})
            return
        body = {
            "item_id": item_id,
            "name": item["name"],
            "quantity_on_hand": item["quantity_on_hand"],
            "available": item["quantity_on_hand"] > 0,
            "pod": POD_NAME,
        }
        print(f"[{POD_NAME}] served item_id={item_id}", flush=True)
        self._send(200, body)

    def log_message(self, fmt, *args):
        return


def main():
    server = ThreadingHTTPServer((HOST, PORT), InventoryHandler)
    print(f"[{POD_NAME}] inventory listening on {HOST}:{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
