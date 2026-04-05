from __future__ import annotations
from functools import wraps
from datetime import datetime

def log_registro_en_terminal(func):
    """
    Decorador para loguear en terminal cuando un registro fue exitoso.
    Asume que la función decorada devuelve un objeto con atributo: ok (bool)
    y que el 1er argumento "real" es nombre_usuario (después de self).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)

        # Detectar nombre_usuario (registro(self, nombre_usuario, ...))
        nombre_usuario = None
        if len(args) >= 2:
            nombre_usuario = args[1]
        else:
            nombre_usuario = kwargs.get("nombre_usuario")

        if getattr(resultado, "ok", False):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Se registró un usuario: {nombre_usuario}")

        return resultado

    return wrapper

def log_cambio_contrasena_terminal(func):
    """
    Decorador: loguea en terminal cuando el cambio de contraseña fue exitoso.
    Asume firma: cambiar_contrasena(self, nombre_usuario, contrasena_actual, nueva1, nueva2)
    y retorno con atributo: ok (bool)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)

        # nombre_usuario suele venir por args[1]
        nombre_usuario = args[1] if len(args) >= 2 else kwargs.get("nombre_usuario")

        if getattr(resultado, "ok", False):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Usuario cambió su contraseña: {nombre_usuario}")

        return resultado

    return wrapper

def log_eliminacion_usuario_terminal(func):
    """
    Decorador: loguea en terminal cuando la eliminación de usuario fue exitosa.
    Asume firma: eliminar_usuario(self, nombre_usuario, contrasena_actual)
    y retorno con atributo: ok (bool)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)

        nombre_usuario = args[1] if len(args) >= 2 else kwargs.get("nombre_usuario")

        if getattr(resultado, "ok", False):
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{ts}] Usuario eliminado: {nombre_usuario}")

        return resultado

    return wrapper