"""
validaciones.py
---------------
reglas de validacion"puras"(sin ui)
devuelven lista de errores, lista vacioa => valido
"""
import re

def contraseña_validaciones_errores(pw:str) -> list [str]:
    errores:list[str]=[]
    if len(pw)<8:
        errores.append(".)Minimo 8 caracteres")
    if not re.search(r"[A-Z]",pw):
        errores.append(".)Al menos 1 mayuscula (A-Z)")
    if not re.search(r"[a-z]",pw):
        errores.append(".)Al menos 1 miniscula (a-z)")
    if not re.search(r"\d",pw):
        errores.append(".)Al menos 1 numero (0-9)")
    if not re.search(r"[^A-Za-z0-9]",pw):
        errores.append(".)Al menos 1 simbolo (ejemplo:@ #$)")

def errores_nombre_de_usuario(nombreUsuario:str) -> list[str]:
    errores:list[str]=[]
    u=nombreUsuario.strip()

    if len(u)<3 or len(u)>20:
        errores.append(".) El usuario debe tener entre 3 y 20 caracteres")

    if not re.fullmatch(r"[A-Za-z0-9._]+",u):
        errores.append(".)Solo se permiten letras,numeros,punto y guion bajo")
        return errores
    
    if u[0] in "._" or u[-1] in"._":
        errores.append(".)No puede empezar ni terminar con '.' o'_'")

    if ".." in u:
        errores.append(".)No se permiten '..' seguidos")
    
    return errores


    

