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