"""
modelo empleado.py
"""
from peewee import Model, CharField
from base_de_datos.db import db

class UsuarioModelo(Model):
    class Meta:
        database=db

class Usuario(UsuarioModelo):
    nombre_usuario=CharField(unique=True)
    contraseña_hash=CharField()
    sector=CharField(default="Linea de produccion")
