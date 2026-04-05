"""
servicios/autentificacion.py

responsabilidad:
- registrar usuarios (con validaciones y hash)
-Loguear usuarios(verificas hash)
-acceder a la db peewee

no muesra qmeesagebox
devuelve resultados estructurados (ok, error,etc) para que el ControladorDeApp decida
que mostrar
"""
from dataclasses import dataclass
from peewee import IntegrityError

from modelo.empleados import Usuario
from seguridad.seguridad import hash_contraseña, verificacion_contraseña
from seguridad.validaciones import errores_nombre_de_usuario, contraseña_validaciones_errores
from servicios.decoradores import log_registro_en_terminal,log_cambio_contrasena_terminal,log_eliminacion_usuario_terminal

@dataclass
class LoginResultado:
    ok:bool
    message:str=""
    errores:list[str] | None = None

class ServicioAutentificacion:
    @log_registro_en_terminal
    def registro(self, nombre_usuario:str,contraseña:str,contraseña2:str)->LoginResultado:
        nombre_usuario = (nombre_usuario or "").strip()
        contraseña=contraseña or ""
        contraseña2=contraseña2 or ""

        #1) campos obligatorios
        if not nombre_usuario or not contraseña or not contraseña2:
            return LoginResultado(False, message="Completa todos los campos")
        
        #2)politicas de usuario
        u_errores= errores_nombre_de_usuario(nombre_usuario)
        if u_errores:
            return LoginResultado(False, message="Usuario Invalidad.", errores = u_errores)
        
        #3) coincidencia de contraseña
        if contraseña != contraseña2:
            return LoginResultado(False, message="La contraseña no coinciden.")
        
        #4) Contraseña  requisitos
        c_errores = contraseña_validaciones_errores(contraseña)
        if c_errores:
            return LoginResultado(False, message="contraseña Invalidad.", errores = c_errores)
        
        #5)crear usuario en db
        try:
            Usuario.create(nombre_usuario=nombre_usuario,contraseña_hash = hash_contraseña(contraseña))
            return LoginResultado(True, message="Usuario creado exitosamente.")
        except IntegrityError:
            return LoginResultado(False, message="Ese nombre de usuario ya fue creado")
        
    def login(self, nombre_usuario: str, contraseña: str) ->LoginResultado:
        nombre_usuario=(nombre_usuario or "" ).strip()
        contraseña=contraseña or ""

        if not nombre_usuario or not contraseña:
            return LoginResultado(False,message="Completar el usuario y/o contraseña")
        
        usuario=Usuario.get_or_none(Usuario.nombre_usuario == nombre_usuario)
        if not usuario:
            return LoginResultado(False,message="Usuario o contraseña incorecta")
        
        if not verificacion_contraseña(contraseña, usuario.contraseña_hash):
            return LoginResultado(False,message="Usuario o contraseña incorecta")
        return LoginResultado(True, message="Login OK")
    @log_cambio_contrasena_terminal
    def cambiar_contrasena(
        self,
        nombre_usuario: str,
        contraseña_actual: str,
        nueva1: str,
        nueva2: str
    ) -> LoginResultado:

        nombre_usuario = (nombre_usuario or "").strip()
        contraseña_actual = contraseña_actual or ""
        nueva1 = nueva1 or ""
        nueva2 = nueva2 or ""

        if not nombre_usuario or not contraseña_actual or not nueva1 or not nueva2:
            return LoginResultado(False, message="Completa todos los campos")

        usuario = Usuario.get_or_none(Usuario.nombre_usuario == nombre_usuario)
        if not usuario:
            return LoginResultado(False, message="Usuario no encontrado")

        if not verificacion_contraseña(contraseña_actual, usuario.contraseña_hash):
            return LoginResultado(False, message="La contraseña actual es incorrecta")

        if nueva1 != nueva2:
            return LoginResultado(False, message="La nueva contraseña no coincide", errores=["No coinciden"])

        c_errores = contraseña_validaciones_errores(nueva1)
        if c_errores:
            return LoginResultado(False, message="Nueva contraseña inválida.", errores=c_errores)

        usuario.contraseña_hash = hash_contraseña(nueva1)
        usuario.save()

        return LoginResultado(True, message="Contraseña actualizada correctamente.")
    @log_eliminacion_usuario_terminal
    def eliminar_usuario(self, nombre_usuario: str, contraseña_actual: str) -> LoginResultado:
        nombre_usuario = (nombre_usuario or "").strip()
        contraseña_actual = contraseña_actual or ""

        if not nombre_usuario or not contraseña_actual:
            return LoginResultado(False, message="Completa todos los campos")

        usuario = Usuario.get_or_none(Usuario.nombre_usuario == nombre_usuario)
        if not usuario:
            return LoginResultado(False, message="Usuario no encontrado")

        if not verificacion_contraseña(contraseña_actual, usuario.contraseña_hash):
            return LoginResultado(False, message="La contraseña actual es incorrecta")

        usuario.delete_instance()
        return LoginResultado(True, message="Usuario eliminado correctamente.")