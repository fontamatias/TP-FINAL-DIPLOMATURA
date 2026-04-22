from dataclasses import dataclass
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
        # Motos que aún no fueron inspeccionadas (las cargadas por producción)
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
        moto.save()
        return InspeccionResultado(True, f"Moto enviada a Mecánica. Motivo: {motivo}")