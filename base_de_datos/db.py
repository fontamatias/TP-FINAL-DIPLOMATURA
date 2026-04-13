"""
db,py
-----
conecxion a slite y helper para iniciarlizar las tablas.
"""
from peewee import SqliteDatabase
from modelo.sectores import SECTOR_POR_DEFECTO

db=SqliteDatabase("Empleados.db")

def empleados_db(models: list[type]) -> None:
    with db:
        db.create_tables(models)
        for model in models:
            if model._meta.table_name != "usuario":
                continue

            columnas = {col.name for col in db.get_columns("usuario")}
            if "sector" not in columnas:
                sector_por_defecto_sql = SECTOR_POR_DEFECTO.replace("'", "''")
                db.execute_sql(
                    f"ALTER TABLE usuario ADD COLUMN sector VARCHAR(255) "
                    f"NOT NULL DEFAULT '{sector_por_defecto_sql}'"
                )
