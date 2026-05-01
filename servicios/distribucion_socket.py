from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from shared.socket_api import SocketAPI
from shared.config import SERVER_HOST, SERVER_PORT
from shared.dtos import MotoDTO, VentaDTO, VentaItemDTO, _parse_dt


@dataclass
class DistribucionResultado:
    ok: bool
    message: str = ""
    errores: list[str] | None = None


class ServicioDistribucionSocket:
    def __init__(self, host: str = SERVER_HOST, port: int = SERVER_PORT):
        self.api = SocketAPI(host, port)

    def listar_stock_listo(self) -> list[MotoDTO]:
        r = self.api.call("listar_stock_listo")
        motos = (r.get("data") or {}).get("motos") or []
        return [
            MotoDTO(
                numero_chasis=m["numero_chasis"],
                numero_motor=m["numero_motor"],
                modelo=m["modelo"],
                color=m["color"],
                estado=m["estado"],
                fecha_hora=_parse_dt(m.get("fecha_hora")),
            )
            for m in motos
        ]

    def listar_ventas_pendientes(self) -> list[VentaDTO]:
        r = self.api.call("listar_ventas_pendientes")
        ventas = (r.get("data") or {}).get("ventas") or []
        return [
            VentaDTO(
                id=int(v["id"]),
                numero_venta=v["numero_venta"],
                fecha_hora=_parse_dt(v.get("fecha_hora")),
                estado=v["estado"],
            )
            for v in ventas
        ]

    def listar_ventas_finalizadas(self) -> list[VentaDTO]:
        r = self.api.call("listar_ventas_finalizadas")
        ventas = (r.get("data") or {}).get("ventas") or []
        return [
            VentaDTO(
                id=int(v["id"]),
                numero_venta=v["numero_venta"],
                fecha_hora=_parse_dt(v.get("fecha_hora")),
                estado=v["estado"],
            )
            for v in ventas
        ]

    def items_de_venta(self, venta_id: int) -> list[VentaItemDTO]:
        r = self.api.call("items_de_venta", {"venta_id": venta_id})
        items = (r.get("data") or {}).get("items") or []
        return [
            VentaItemDTO(
                id=int(it["id"]),
                venta_id=it.get("venta_id"),
                numero_chasis=it["numero_chasis"],
                numero_motor=it["numero_motor"],
            )
            for it in items
        ]

    def crear_venta_pendiente(self) -> VentaDTO:
        r = self.api.call("crear_pedido")
        if not r.get("ok"):
            raise RuntimeError(r.get("message") or "No se pudo crear pedido.")
        v = (r.get("data") or {}).get("venta") or {}
        return VentaDTO(
            id=int(v["id"]),
            numero_venta=v["numero_venta"],
            fecha_hora=_parse_dt(v.get("fecha_hora")),
            estado=v["estado"],
        )

    def agregar_moto_a_venta(self, venta_id: int, chasis: str) -> DistribucionResultado:
        r = self.api.call("agregar_moto_a_pedido", {"venta_id": venta_id, "chasis": chasis})
        return DistribucionResultado(bool(r.get("ok")), r.get("message") or "")

    def finalizar_venta(self, venta_id: int) -> DistribucionResultado:
        r = self.api.call("finalizar_venta", {"venta_id": venta_id})
        return DistribucionResultado(bool(r.get("ok")), r.get("message") or "")

    def ventas_finalizadas_del_dia(self, dia: date) -> int:
        r = self.api.call("ventas_finalizadas_del_dia", {"dia": dia.isoformat()})
        return int(((r.get("data") or {}).get("count")) or 0)

    def motos_vendidas_del_dia(self, dia: date) -> int:
        r = self.api.call("motos_vendidas_del_dia", {"dia": dia.isoformat()})
        return int(((r.get("data") or {}).get("count")) or 0)