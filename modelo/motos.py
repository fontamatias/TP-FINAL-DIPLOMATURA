"""
modelo/motos.py
------------------
modelo peewee para motos declaradas en produccion
"""

from peewee import Model, CharField, DateTimeField
from datetime import datetime
from base_de_datos.db import db

INSPECCION_PENDIENTE = "PENDIENTE"
INSPECCION_OK = "OK"
INSPECCION_NO_OK = "NO_OK"

class MotoModelo(Model):
    class Meta:
        database = db
        table_name="Motos"

class Moto(MotoModelo):
    numero_chasis = CharField(unique = True)
    numero_motor = CharField(unique = True)
    modelo = CharField ()
    color = CharField ()
    fecha_hora = DateTimeField (default = datetime.now)
    estado_inspeccion = CharField(default=INSPECCION_PENDIENTE)
    motivo_no_ok = CharField(null=True, default=None, max_length=200)
    fecha_inspeccion = DateTimeField(null=True, default=None)