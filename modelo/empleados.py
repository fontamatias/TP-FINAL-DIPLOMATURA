"""
modelo empleado.py
"""
from peewee import Model, CharField
from base_de_datos.login import db

class UsuarioModelo(Model):
    class Meta:
        database=db

class Usuario(UsuarioModelo):
    nombreUsuario=CharField(unique=True)
    contraseña_hash=CharField()