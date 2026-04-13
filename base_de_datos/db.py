"""
db.py
-----
conexión a sqlite y helper para inicializar las tablas.
"""
from peewee import SqliteDatabase, CharField
from playhouse.migrate import SqliteMigrator, migrate

db=SqliteDatabase("Empleados.db")

def empleados_db(models: list[type]) -> None:
    with db:
        db.create_tables(models)
        _asegurar_columna_sector()

def _asegurar_columna_sector() -> None:
    if "usuario" not in db.get_tables():
        return

    columnas = {col.name for col in db.get_columns("usuario")}
    if "sector" in columnas:
        return

    migrator = SqliteMigrator(db)
    migrate(
        migrator.add_column(
            "usuario",
            "sector",
            CharField(max_length=60, default="Línea producción (declaración)"),
        )
    )
