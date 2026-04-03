"""
db,py
-----
conecxion a slite y helper para iniciarlizar las tablas.
"""
from peewee import SqliteDatabase

db=SqliteDatabase("Empleados.db")

def empleados_db(models: list[type]) -> None:
    db.connect(reuse_if_open=True)
    db.create_tables(models)