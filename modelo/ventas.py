from __future__ import annotations

from datetime import datetime
from peewee import Model, CharField, DateTimeField, ForeignKeyField

from base_de_datos.db import db
from modelo.motos import Moto


class VentaModelo(Model):
    class Meta:
        database = db
        table_name = "Ventas"


class Venta(VentaModelo):
    # número random de 5 dígitos, NO repetible
    numero_venta = CharField(unique=True)
    fecha_hora = DateTimeField(default=datetime.now)
    estado = CharField(default="PENDIENTE")  # PENDIENTE | FINALIZADA


class VentaItemModelo(Model):
    class Meta:
        database = db
        table_name = "VentaItems"


class VentaItem(VentaItemModelo):
    venta = ForeignKeyField(Venta, backref="items", on_delete="CASCADE")
    moto = ForeignKeyField(Moto, backref="venta_items", null=True, on_delete="SET NULL")

    # snapshot (para que quede registrado aunque cambie algo)
    numero_chasis = CharField()
    numero_motor = CharField()