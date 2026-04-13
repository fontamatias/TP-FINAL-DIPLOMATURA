"""
db,py
-----
conecxion a slite y helper para iniciarlizar las tablas.
"""
from peewee import SqliteDatabase, CharField
from playhouse.migrate import SqliteMigrator, migrate
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
                migrator = SqliteMigrator(db)
                migrate(
                    migrator.add_column(
                        "usuario",
                        "sector",
                        CharField(default=SECTOR_POR_DEFECTO),
                    )
                )
