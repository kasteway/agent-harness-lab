"""Tiny read-only HTTP API over the same approved functions as the MCP server.

This is deliberately a plain API, not an MCP endpoint. It gives the client a
fixed URL and request format; it does not offer MCP tool discovery.
"""

import json
import socketserver
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .tools import execute


class ToolAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/tools/compare_sla":
            self._send(404, {"error": "unknown endpoint"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                raise ValueError("request body must be 1-4096 bytes")
            args = json.loads(self.rfile.read(size))
            if not isinstance(args, dict):
                raise ValueError("request body must be a JSON object")
            self._send(200, execute("compare_sla", args))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, {"error": str(exc)})

    def _send(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Keep the learning output focused on the request and result.


class LocalHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        # Avoid a reverse-DNS lookup when binding the loopback address.
        socketserver.TCPServer.server_bind(self)
        self.server_name = "localhost"
        self.server_port = self.server_address[1]


def make_server():
    # Loopback only: this tutorial never exposes its sample API to a network.
    return LocalHTTPServer(("127.0.0.1", 0), ToolAPIHandler)
