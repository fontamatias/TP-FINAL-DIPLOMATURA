from __future__ import annotations

import json
from typing import Any


def read_json_line(conn_file) -> dict[str, Any] | None:
    line = conn_file.readline()
    if not line:
        return None
    line = line.decode("utf-8").strip()
    if not line:
        return None
    return json.loads(line)


def write_json_line(conn_file, payload: dict[str, Any]) -> None:
    raw = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
    conn_file.write(raw)
    conn_file.flush()