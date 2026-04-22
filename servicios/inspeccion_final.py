from dataclasses import dataclass
from datetime import datetime, date

from modelo.motos import Moto

MOTIVOS_NO_OK = [
    "Marca en encadenado",
    "Error mecánico",
    "Error eléctrico",
    "Otros",
]


@dataclass
class InspeccionResultado:
    ok: bool
    message: str = ""
    errores: list[str] | None = None


class ServicioInspeccionFinal:
    def listar_pendientes(self) -> list[Moto]:
        # pendientes de inspección final: las que están "en producción"
        return list(
            Moto.select()
            .where(Moto.estado == "EN_PRODUCCION")
            .order_by(Moto.fecha_hora.desc())
        )

    def marcar_ok(self, chasis: str) -> InspeccionResultado:
        chasis = (chasis or "").strip()
        if not chasis:
            return InspeccionResultado(False, "Seleccioná una moto (chasis).")

        moto = Moto.get_or_none(Moto.numero_chasis == chasis)
        if not moto:
            return InspeccionResultado(False, "Moto no encontrada.")

        moto.estado = "OK_INSPECCION"
        moto.motivo_rechazo = None
        moto.fecha_inspeccion_final = datetime.now()
        moto.save()
        return InspeccionResultado(True, "Moto marcada como OK (Inspección final).")

    def marcar_no_ok(self, chasis: str, motivo: str) -> InspeccionResultado:
        chasis = (chasis or "").strip()
        motivo = (motivo or "").strip()

        if not chasis:
            return InspeccionResultado(False, "Seleccioná una moto (chasis).")

        if not motivo:
            return InspeccionResultado(False, "Seleccioná un motivo.")

        if motivo not in MOTIVOS_NO_OK:
            return InspeccionResultado(False, "Motivo inválido.")

        moto = Moto.get_or_none(Moto.numero_chasis == chasis)
        if not moto:
            return InspeccionResultado(False, "Moto no encontrada.")

        moto.estado = "A_MECANICA"
        moto.motivo_rechazo = motivo
        moto.fecha_inspeccion_final = datetime.now()
        moto.save()
        return InspeccionResultado(True, f"Moto enviada a Mecánica. Motivo: {motivo}")

    # ===== cierre de día inspección final =====
    def cantidad_ok_del_dia(self, dia: date) -> int:
        inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
        fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)

        return (
            Moto.select()
            .where(
                (Moto.estado == "OK_INSPECCION")
                & (Moto.fecha_inspeccion_final.is_null(False))
                & (Moto.fecha_inspeccion_final >= inicio)
                & (Moto.fecha_inspeccion_final <= fin)
            )
            .count()
        )

    def cantidad_no_ok_del_dia(self, dia: date) -> int:
        inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
        fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)

        return (
            Moto.select()
            .where(
                (Moto.estado == "A_MECANICA")
                & (Moto.fecha_inspeccion_final.is_null(False))
                & (Moto.fecha_inspeccion_final >= inicio)
                & (Moto.fecha_inspeccion_final <= fin)
            )
            .count()
        )