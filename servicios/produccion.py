"""
servicios/produccion.py
-----------------------
Lógica de negocio para declarar/buscar/modificar motos.
No depende de UI.
"""
from dataclasses import dataclass
from datetime import datetime, date
from peewee import IntegrityError

from modelo.motos import Moto

MODELOS_COLORES = {
    "110": ["Azul", "Roja"],
    "150": ["Negra", "Blanca"],
}


@dataclass
class ProduccionResultado:
    ok: bool
    message: str = ""
    errores: list[str] | None = None


class ServicioProduccion:
    def colores_para_modelo(self, modelo: str) -> list[str]:
        return MODELOS_COLORES.get(modelo, [])

    def declarar_moto(self, chasis: str, motor: str, modelo: str, color: str) -> ProduccionResultado:
        chasis = (chasis or "").strip()
        motor = (motor or "").strip()
        modelo = (modelo or "").strip()
        color = (color or "").strip()

        errores: list[str] = []
        if not chasis or not motor or not modelo or not color:
            return ProduccionResultado(False, "Completa todos los campos")

        if modelo not in MODELOS_COLORES:
            errores.append("Modelo inválido (solo 110 o 150).")

        if modelo in MODELOS_COLORES and color not in MODELOS_COLORES[modelo]:
            errores.append(f"Color inválido para modelo {modelo}.")

        if errores:
            return ProduccionResultado(False, "Datos inválidos.", errores=errores)

        try:
            Moto.create(
                numero_chasis=chasis,
                numero_motor=motor,
                modelo=modelo,
                color=color,
                fecha_hora=datetime.now(),
                estado="EN_PRODUCCION",
                motivo_rechazo=None,
                fecha_inspeccion_final=None,
            )
            return ProduccionResultado(True, "Moto declarada correctamente.")
        except IntegrityError:
            return ProduccionResultado(False, "El número de chasis o motor ya existe.")

    def modificar_moto_por_chasis(self, chasis: str, motor: str, modelo: str, color: str) -> ProduccionResultado:
        chasis = (chasis or "").strip()
        motor = (motor or "").strip()
        modelo = (modelo or "").strip()
        color = (color or "").strip()

        if not chasis:
            return ProduccionResultado(False, "Seleccioná una moto (chasis).")

        moto = Moto.get_or_none(Moto.numero_chasis == chasis)
        if not moto:
            return ProduccionResultado(False, "Moto no encontrada.")

        errores: list[str] = []
        if not motor or not modelo or not color:
            return ProduccionResultado(False, "Completa todos los campos.")

        if modelo not in MODELOS_COLORES:
            errores.append("Modelo inválido (solo 110 o 150).")

        if modelo in MODELOS_COLORES and color not in MODELOS_COLORES[modelo]:
            errores.append(f"Color inválido para modelo {modelo}.")

        if errores:
            return ProduccionResultado(False, "Datos inválidos.", errores=errores)

        try:
            moto.numero_motor = motor
            moto.modelo = modelo
            moto.color = color
            moto.fecha_hora = datetime.now()
            moto.save()
            return ProduccionResultado(True, "Moto modificada correctamente.")
        except IntegrityError:
            return ProduccionResultado(False, "El número de motor ya existe en otra moto.")

    def buscar(self, texto: str) -> list[Moto]:
        t = (texto or "").strip()
        if not t:
            return list(Moto.select().order_by(Moto.fecha_hora.desc()))

        return list(
            Moto.select()
            .where((Moto.numero_chasis.contains(t)) | (Moto.numero_motor.contains(t)))
            .order_by(Moto.fecha_hora.desc())
        )

    # === NUEVO: búsquedas/listados por estado ===
    def listar_por_estado(self, estado: str) -> list[Moto]:
        estado = (estado or "").strip()
        if not estado or estado == "TODOS":
            return self.listar_todas()

        return list(
            Moto.select()
            .where(Moto.estado == estado)
            .order_by(Moto.fecha_hora.desc())
        )

    def buscar_por_estado(self, texto: str, estado: str) -> list[Moto]:
        t = (texto or "").strip()
        estado = (estado or "").strip()

        q = Moto.select()

        if estado and estado != "TODOS":
            q = q.where(Moto.estado == estado)

        if t:
            q = q.where((Moto.numero_chasis.contains(t)) | (Moto.numero_motor.contains(t)))

        return list(q.order_by(Moto.fecha_hora.desc()))

    def listar_todas(self) -> list[Moto]:
        return list(Moto.select().order_by(Moto.fecha_hora.desc()))

    def cantidad_del_dia(self, dia: date) -> int:
        inicio = datetime(dia.year, dia.month, dia.day, 0, 0, 0)
        fin = datetime(dia.year, dia.month, dia.day, 23, 59, 59, 999999)
        return Moto.select().where((Moto.fecha_hora >= inicio) & (Moto.fecha_hora <= fin)).count()