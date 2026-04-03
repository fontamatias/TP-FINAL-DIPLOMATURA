"""
seguridad.py
-----------
Funciones de seguridad (hash y verificacion).
(logica reutilizable: no de pende de ui)
"""
import bcrypt

def hash_contraseña(constraseña: str) -> str:
    salt=bcrypt.gensalt(rounds=12)
    hashed=bcrypt.hashpw(constraseña.encode("utf-8"),salt)
    return hashed.decode("utf-8")

def verificacion_contraseña(constraseña:str,stored_hash:str)-> bool:
    return bcrypt.checkpw(constraseña.encode("utf-8"),
                          stored_hash.encode("utf-8"))