from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
import random

from peewee import IntegrityError

from modelo.motos import Moto
from modelo.ventas import Venta, VentaItem


@dataclass
class DistribucionResultado:
    ok: bool
    message: str = ""
    errores: list[str] | None = None


class ServicioDistribucion:
    # stock listo para venta (OK de inspección final)
    def listar_stock_listo(self) -> list[Moto]:
        return list(
            Moto.select()
            .where(Moto.estado == "OK_INSPECCION")
            .order_by(Moto.fecha_hora.desc())
        )

    # pedidos/ventas pendientes (aún no finalizadas)
    def listar_ventas_pendientes(self) -> list[Venta]:
        return list(
            Venta.select()
            .where(Venta.estado == "PENDIENTE")
            .order_by(Venta.fecha_hora.desc())
        )

    # NUEVO: historial (ventas finalizadas)
    def listar_ventas_finalizadas(self) -> list[Venta]:
        return list(
            Venta.select()
            .where(Venta.estado == "FINALIZADA")
            .order_by(Venta.fecha_hora.desc())
        )

    def _generar_numero_venta_5_digitos(self) -> str:
        return str(random.randint(10000, 99999))

    def crear_venta_pendiente(self) -> Venta:
        for _ in range(50):
            numero = self._generar_numero_venta_5_digitos()
            try:
                return Venta.create(numero_venta=numero, fecha_hora=datetime.now(), estado="PENDIENTE")
            except IntegrityError:
                continue
        raise RuntimeError("No se pudo generar un número de venta único (intentos agotados).")

    def agregar_moto_a_venta(self, venta_id: int, chasis: str) -> DistribucionResultado:
        chasis = (chasis or "").strip()
        if not chasis:
            return DistribucionResultado(False, "Seleccioná una moto (chasis).")

        venta = Venta.get_or_none(Venta.id == venta_id)
        if not venta:
            return DistribucionResultado(False, "Venta no encontrada.")

        if venta.estado != "PENDIENTE":
            return DistribucionResultado(False, "La venta ya fue finalizada.")

        moto = Moto.get_or_none(Moto.numero_chasis == chasis)
        if not moto:
            return DistribucionResultado(False, "Moto no encontrada.")

        if moto.estado != "OK_INSPECCION":
            return DistribucionResultado(False, "La moto no está lista para distribución (debe estar OK_INSPECCION).")

        ya = (
            VentaItem.select()
            .where((VentaItem.venta == venta) & (VentaItem.numero_chasis == moto.numero_chasis))
            .exists()
        )
        if ya:
            return DistribucionResultado(False, "Esa moto ya está en la venta.")

        VentaItem.create(
            venta=venta,
            moto=moto,
            numero_chasis=moto.numero_chasis,
            numero_motor=moto.numero_motor,
        )
        return DistribucionResultado(True, "Moto agregada al pedido.")

    def items_de_venta(self, venta_id: int) -> list[VentaItem]:
        venta = Venta.get_or_none(Venta.id == venta_id)
        if not venta:
            return []
        return list(VentaItem.select().where(VentaItem.venta == venta))

    def finalizar_venta(self, venta_id: int) -> DistribucionResultado:
        venta = Venta.get_or_none(Venta.id == venta_id)
        if not venta:
            return DistribucionResultado(False, "Venta no encontrada.")

        if venta.estado != "PENDIENTE":
            return DistribucionResultado(False, "La venta ya estaba finalizada.")

        items = list(VentaItem.select().where(VentaItem.venta == venta))
        if not items:
            return DistribucionResultado(False, "La venta no tiene motos cargadas.")

        for it in items:
            moto = it.moto
            if moto is None:
                continue
            moto.estado = "VENDIDA"
            moto.save()

        venta.estado = "FINALIZADA"
        venta.fecha_hora = datetime.now()
        venta.save()

        return DistribucionResultado(True, f"Venta {venta.numero_venta} finalizada. Motos marcadas como VENDIDA.")

    # NUEVO: cierre de día distribución
    def ventas_finalizadas_del_dia(self, dia: date) -> int:
        inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
        fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)

        return (
            Venta.select()
            .where(
                (Venta.estado == "FINALIZADA")
                & (Venta.fecha_hora >= inicio)
                & (Venta.fecha_hora <= fin)
            )
            .count()
        )

    # opcional: cuántas motos salieron hoy en total
    def motos_vendidas_del_dia(self, dia: date) -> int:
        inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
        fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)

        # cuenta items de ventas finalizadas hoy
        return (
            VentaItem.select()
            .join(Venta)
            .where(
                (Venta.estado == "FINALIZADA")
                & (Venta.fecha_hora >= inicio)
                & (Venta.fecha_hora <= fin)
            )
            .count()
        )