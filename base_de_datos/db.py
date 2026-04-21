"""
db,py
-----
conecxion a slite y helper para iniciarlizar las tablas.
"""
from pathlib import Path
from peewee import SqliteDatabase

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR=BASE_DIR/"data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR/"Empleados.db"
db=SqliteDatabase(str(DB_PATH))

def empleados_db(models: list[type]) -> None:
    with db:
        db.create_tables(models)

def migrar_motos() -> None:
    """Agrega columnas nuevas al modelo Moto si no existen (migración incremental)."""
    nuevas_columnas = [
        ("estado_inspeccion", "VARCHAR(20)", "DEFAULT 'PENDIENTE'"),
        ("motivo_no_ok", "VARCHAR(200)", ""),
        ("fecha_inspeccion", "DATETIME", ""),
    ]
    with db:
        cursor = db.execute_sql("PRAGMA table_info(Motos)")
        columnas_existentes = {row[1] for row in cursor.fetchall()}
        for nombre, tipo, extra in nuevas_columnas:
            if nombre not in columnas_existentes:
                sql = f"ALTER TABLE Motos ADD COLUMN {nombre} {tipo}"
                if extra:
                    sql = f"{sql} {extra}"
                db.execute_sql(sql)