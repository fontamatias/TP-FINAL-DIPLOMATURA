"""
servicios/inspeccion_final.py
------------------------------
Lógica de negocio para la inspección final de motos.
No depende de UI.
"""
from dataclasses import dataclass
from datetime import datetime

from modelo.motos import Moto, INSPECCION_OK, INSPECCION_NO_OK, INSPECCION_PENDIENTE

MOTIVOS_NO_OK = [
    "Marca en cadenado",
    "Error mecánico",
    "Error eléctrico",
    "Otros",
]


@dataclass
class InspeccionResultado:
    ok: bool
    message: str = ""


class ServicioInspeccionFinal:

    def listar_todas(self) -> list[Moto]:
        return list(Moto.select().order_by(Moto.fecha_hora.desc()))

    def listar_pendientes(self) -> list[Moto]:
        return list(
            Moto.select()
            .where(Moto.estado_inspeccion == INSPECCION_PENDIENTE)
            .order_by(Moto.fecha_hora.desc())
        )

    def marcar_ok(self, chasis: str) -> InspeccionResultado:
        chasis = (chasis or "").strip()
        if not chasis:
            return InspeccionResultado(False, "Chasis no especificado.")

        moto = Moto.get_or_none(Moto.numero_chasis == chasis)
        if not moto:
            return InspeccionResultado(False, "Moto no encontrada.")

        moto.estado_inspeccion = INSPECCION_OK
        moto.motivo_no_ok = None
        moto.fecha_inspeccion = datetime.now()
        moto.save()
        return InspeccionResultado(True, "Moto aprobada (OK). Disponible para Distribución.")

    def marcar_no_ok(self, chasis: str, motivo: str) -> InspeccionResultado:
        chasis = (chasis or "").strip()
        motivo = (motivo or "").strip()
        if not chasis:
            return InspeccionResultado(False, "Chasis no especificado.")
        if not motivo:
            return InspeccionResultado(False, "Debe indicar un motivo.")

        moto = Moto.get_or_none(Moto.numero_chasis == chasis)
        if not moto:
            return InspeccionResultado(False, "Moto no encontrada.")

        moto.estado_inspeccion = INSPECCION_NO_OK
        moto.motivo_no_ok = motivo
        moto.fecha_inspeccion = datetime.now()
        moto.save()
        return InspeccionResultado(True, f"Moto derivada a Mecánica. Motivo: {motivo}.")
