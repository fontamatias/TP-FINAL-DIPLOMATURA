from __future__ import annotations

import socket
import json
from typing import Any


class SocketAPI:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout

    def call(self, action: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {"action": action, "data": data or {}}

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect((self.host, self.port))

        with s:
            f = s.makefile("rwb")
            f.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
            f.flush()

            line = f.readline()
            if not line:
                return {"ok": False, "message": "Sin respuesta del servidor.", "data": {}}
            return json.loads(line.decode("utf-8"))