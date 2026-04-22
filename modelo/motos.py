"""
modelo/motos.py
------------------
modelo peewee para motos declaradas en produccion
"""

from peewee import Model, CharField, DateTimeField
from datetime import datetime
from base_de_datos.db import db


class MotoModelo(Model):
    class Meta:
        database = db
        table_name = "Motos"


class Moto(MotoModelo):
    numero_chasis = CharField(unique=True)
    numero_motor = CharField(unique=True)
    modelo = CharField()
    color = CharField()
    fecha_hora = DateTimeField(default=datetime.now)
    estado = CharField(default="EN_PRODUCCION")
    motivo_rechazo = CharField(null=True)