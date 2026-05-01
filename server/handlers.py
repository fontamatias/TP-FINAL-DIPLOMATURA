from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, date
from typing import Any

from peewee import IntegrityError

from base_de_datos.db import db
from modelo.motos import Moto
from modelo.ventas import Venta, VentaItem


def ok(data: dict[str, Any] | None = None, message: str = "") -> dict[str, Any]:
    return {"ok": True, "message": message, "data": data or {}}


def err(message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": False, "message": message, "data": data or {}}


def _venta_to_dict(v: Venta) -> dict[str, Any]:
    return {
        "id": v.id,
        "numero_venta": v.numero_venta,
        "fecha_hora": v.fecha_hora.isoformat(sep=" "),
        "estado": v.estado,
    }


def _moto_to_dict(m: Moto) -> dict[str, Any]:
    return {
        "numero_chasis": m.numero_chasis,
        "numero_motor": m.numero_motor,
        "modelo": str(m.modelo),
        "color": str(m.color),
        "estado": m.estado,
        "fecha_hora": m.fecha_hora.isoformat(sep=" ") if m.fecha_hora else None,
    }


def _venta_item_to_dict(it: VentaItem) -> dict[str, Any]:
    return {
        "id": it.id,
        "venta_id": it.venta.id if it.venta else None,
        "numero_chasis": it.numero_chasis,
        "numero_motor": it.numero_motor,
    }


def handle(action: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Dispatcher de acciones del servidor.
    Cada handler abre conexión a DB si hace falta.
    """
    db.connect(reuse_if_open=True)
    try:
        if action == "ping":
            return ok({"pong": True})

        # ======== CATÁLOGO / STOCK (cliente comprador) ========
        if action == "listar_stock_listo":
            motos = list(
                Moto.select()
                .where(Moto.estado == "OK_INSPECCION")
                .order_by(Moto.fecha_hora.desc())
            )
            return ok({"motos": [_moto_to_dict(m) for m in motos]})

        if action == "stock_resumen_por_modelo_color":
            # devuelve resumen de stock OK_INSPECCION por (modelo, color)
            rows = {}
            motos = Moto.select().where(Moto.estado == "OK_INSPECCION")
            for m in motos:
                key = (str(m.modelo), str(m.color))
                rows[key] = rows.get(key, 0) + 1
            resumen = [{"modelo": k[0], "color": k[1], "cantidad": v} for k, v in sorted(rows.items())]
            return ok({"resumen": resumen})

        # ======== PEDIDOS (cliente comprador) ========
        if action == "crear_pedido":
            """
            Crea una venta pendiente vacía (pedido) y devuelve id + nro.
            """
            # genera nro 5 dígitos (similar a tu servicio)
            import random
            for _ in range(50):
                numero = str(random.randint(10000, 99999))
                try:
                    v = Venta.create(numero_venta=numero, fecha_hora=datetime.now(), estado="PENDIENTE")
                    return ok({"venta": _venta_to_dict(v)}, "Pedido creado.")
                except IntegrityError:
                    continue
            return err("No se pudo generar un número de venta único (intentos agotados).")

        if action == "agregar_moto_a_pedido":
            """
            data: {venta_id:int, chasis:str}
            Regla: solo permite agregar motos OK_INSPECCION y las pasa a estado 'RESERVADA'
            para que no aparezcan disponibles para otros pedidos.
            """
            venta_id = int(data.get("venta_id") or 0)
            chasis = (data.get("chasis") or "").strip()
            if not venta_id:
                return err("venta_id requerido.")
            if not chasis:
                return err("chasis requerido.")

            v = Venta.get_or_none(Venta.id == venta_id)
            if not v:
                return err("Venta no encontrada.")
            if v.estado != "PENDIENTE":
                return err("La venta no está pendiente.")

            m = Moto.get_or_none(Moto.numero_chasis == chasis)
            if not m:
                return err("Moto no encontrada.")

            if m.estado != "OK_INSPECCION":
                return err("La moto no está disponible (debe estar OK_INSPECCION).")

            # ya está en el pedido?
            ya = (
                VentaItem.select()
                .where((VentaItem.venta == v) & (VentaItem.numero_chasis == m.numero_chasis))
                .exists()
            )
            if ya:
                return err("Esa moto ya está en el pedido.")

            # transacción: crear item + reservar moto
            with db.atomic():
                VentaItem.create(
                    venta=v,
                    moto=m,
                    numero_chasis=m.numero_chasis,
                    numero_motor=m.numero_motor,
                )
                m.estado = "RESERVADA"
                m.save()

            return ok({}, "Moto agregada y reservada.")

        if action == "items_de_venta":
            venta_id = int(data.get("venta_id") or 0)
            v = Venta.get_or_none(Venta.id == venta_id)
            if not v:
                return ok({"items": []})
            items = list(VentaItem.select().where(VentaItem.venta == v))
            return ok({"items": [_venta_item_to_dict(it) for it in items]})

        # ======== DISTRIBUCIÓN (app interna) ========
        if action == "listar_ventas_pendientes":
            ventas = list(
                Venta.select()
                .where(Venta.estado == "PENDIENTE")
                .order_by(Venta.fecha_hora.desc())
            )
            return ok({"ventas": [_venta_to_dict(v) for v in ventas]})

        if action == "listar_ventas_finalizadas":
            ventas = list(
                Venta.select()
                .where(Venta.estado == "FINALIZADA")
                .order_by(Venta.fecha_hora.desc())
            )
            return ok({"ventas": [_venta_to_dict(v) for v in ventas]})

        if action == "finalizar_venta":
            venta_id = int(data.get("venta_id") or 0)
            v = Venta.get_or_none(Venta.id == venta_id)
            if not v:
                return err("Venta no encontrada.")
            if v.estado != "PENDIENTE":
                return err("La venta ya estaba finalizada.")

            items = list(VentaItem.select().where(VentaItem.venta == v))
            if not items:
                return err("La venta no tiene motos cargadas.")

            with db.atomic():
                for it in items:
                    moto = it.moto
                    if moto is None:
                        continue
                    # de RESERVADA -> VENDIDA (o OK_INSPECCION -> VENDIDA)
                    moto.estado = "VENDIDA"
                    moto.save()

                v.estado = "FINALIZADA"
                v.fecha_hora = datetime.now()
                v.save()

            return ok({}, f"Venta {v.numero_venta} finalizada.")

        if action == "ventas_finalizadas_del_dia":
            dia_iso = (data.get("dia") or "").strip()
            if not dia_iso:
                return err("dia requerido (YYYY-MM-DD).")
            y, m, d = [int(x) for x in dia_iso.split("-")]
            dia = date(y, m, d)

            inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
            fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)

            count = (
                Venta.select()
                .where((Venta.estado == "FINALIZADA") & (Venta.fecha_hora >= inicio) & (Venta.fecha_hora <= fin))
                .count()
            )
            return ok({"count": count})

        if action == "motos_vendidas_del_dia":
            dia_iso = (data.get("dia") or "").strip()
            if not dia_iso:
                return err("dia requerido (YYYY-MM-DD).")
            y, m, d = [int(x) for x in dia_iso.split("-")]
            dia = date(y, m, d)

            inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
            fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)

            count = (
                VentaItem.select()
                .join(Venta)
                .where((Venta.estado == "FINALIZADA") & (Venta.fecha_hora >= inicio) & (Venta.fecha_hora <= fin))
                .count()
            )
            return ok({"count": count})

        return err(f"Acción desconocida: {action}")

    except Exception as e:
        return err(f"Error interno: {e}")
    finally:
        if not db.is_closed():
            db.close()