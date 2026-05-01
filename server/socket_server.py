from __future__ import annotations

import socket
import threading

from server.protocol import read_json_line, write_json_line
from server.handlers import handle


class SocketServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 9009):
        self.host = host
        self.port = port

    def serve_forever(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(50)

        print(f"[SERVER] escuchando en {self.host}:{self.port}")

        while True:
            conn, addr = srv.accept()
            print(f"[SERVER] conexión de {addr}")
            t = threading.Thread(target=self._client_thread, args=(conn, addr), daemon=True)
            t.start()

    def _client_thread(self, conn: socket.socket, addr):
        with conn:
            conn_file = conn.makefile("rwb")
            while True:
                req = read_json_line(conn_file)
                if req is None:
                    print(f"[SERVER] {addr} desconectó")
                    return

                action = req.get("action", "")
                data = req.get("data") or {}
                resp = handle(action, data)
                write_json_line(conn_file, resp)


if __name__ == "__main__":
    SocketServer(host="0.0.0.0", port=9009).serve_forever()