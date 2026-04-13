"""
db,py
-----
conecxion a slite y helper para iniciarlizar las tablas.
"""
from peewee import SqliteDatabase

db=SqliteDatabase("Empleados.db")
SECTOR_POR_DEFECTO = "Linea de produccion"

def empleados_db(models: list[type]) -> None:
    with db:
        db.create_tables(models)
        for model in models:
            if model._meta.table_name != "usuario":
                continue

            columnas = {col.name for col in db.get_columns("usuario")}
            if "sector" not in columnas:
                db.execute_sql(
                    f"ALTER TABLE usuario ADD COLUMN sector VARCHAR(255) "
                    f"NOT NULL DEFAULT '{SECTOR_POR_DEFECTO}'"
                )
