from dataclasses import dataclass
from datetime import datetime, date

from modelo.motos import Moto


@dataclass
class MecanicaResultado:
    ok: bool
    message: str = ""
    errores: list[str] | None = None


class ServicioMecanica:
    def listar_en_mecanica(self) -> list[Moto]:
        return list(
            Moto.select()
            .where(Moto.estado == "A_MECANICA")
            .order_by(Moto.fecha_hora.desc())
        )

    def dar_alta(self, chasis: str) -> MecanicaResultado:
        chasis = (chasis or "").strip()
        if not chasis:
            return MecanicaResultado(False, "Seleccioná una moto (chasis).")

        moto = Moto.get_or_none(Moto.numero_chasis == chasis)
        if not moto:
            return MecanicaResultado(False, "Moto no encontrada.")

        if moto.estado != "A_MECANICA":
            return MecanicaResultado(False, "La moto no está en Mecánica.")

        moto.estado = "EN_PRODUCCION"        # vuelve a Inspección Final
        moto.motivo_rechazo = None
        moto.fecha_reparacion = datetime.now()
        moto.save()

        return MecanicaResultado(True, "Moto reparada. Vuelve a Inspección Final.")

    def cantidad_reparadas_del_dia(self, dia: date) -> int:
        inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
        fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)

        return (
            Moto.select()
            .where(
                (Moto.fecha_reparacion.is_null(False))
                & (Moto.fecha_reparacion >= inicio)
                & (Moto.fecha_reparacion <= fin)
            )
            .count()
        )