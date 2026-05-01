from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    # Soporta "YYYY-MM-DD HH:MM:SS" y "YYYY-MM-DDTHH:MM:SS"
    return datetime.fromisoformat(s)


@dataclass
class MotoDTO:
    numero_chasis: str
    numero_motor: str
    modelo: str
    color: str
    estado: str
    fecha_hora: datetime | None


@dataclass
class VentaDTO:
    id: int
    numero_venta: str
    fecha_hora: datetime | None
    estado: str


@dataclass
class VentaItemDTO:
    id: int
    venta_id: int | None
    numero_chasis: str
    numero_motor: str