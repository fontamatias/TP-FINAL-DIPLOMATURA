"""
controlador/app_contolador.py
-----------------------------
controlador principal

responsabilidad:
-mostrar login
-si el usuario pide registro, abrir NuevoRegistro
-usar IngresoSistema para registrar/logear
-mostrar mensajes en UI (QMessageBox)
-si el login esta ok, abrir MenuEmpleados

la UI no toca peewee/bcrypt: solo llama a metodos del app_controlador.py

"""
from PyQt6.QtWidgets import QMessageBox

from servicios.autentificacion import ServicioAutentificacion
from ui.loginUi import PresentacionLogin
from ui.registroUi import VistaRegistro
from ui.Bienvenida import BienvenidoApp
from ui.cambiarCC import VistaCambiarContraseña





class ControladordDeApp:
    def __init__(self):
        self.autentificacion= ServicioAutentificacion()
        self.ventana_bienvenido = None # mantener referencia para no se destruya

    def arranque(self) -> int:
        """
        ejecuta el flujo general
        retorna:
        0 si el usario cancela/cierra el login
        1 si entra exitosamente
        """
        login = PresentacionLogin()
        #conectamos acciones de la vista a metods del contolador
        login.on_login = lambda u, c:self.manejar_login(login,u,c)
        login.on_abrir_registro =lambda:self.abrir_registro(login)
        login.on_cambiar_contraseñacambiar_contraseña=lambda:self.abrir_cambiar_contraseña(login)
        resultado = login.exec()

        if resultado == PresentacionLogin.DialogCode.Accepted:
            #si el dialogo acepto, el controlador ya abrio Ventana de Bienvenida
            return 1
        return 0
    
    def abrir_registro(self,diaologo_login:PresentacionLogin)->None:
        """
        Abre el registro. si se registra ok, precarga username en login"""

        reg = VistaRegistro()

        #conecta accion con crear cuenta
        reg.activar_registro=lambda u,c1,c2:self.manejar_registro(reg,u,c1,c2)

        if reg.exec() == VistaRegistro.DialogCode.Accepted:
            #precargamos username en el login (comodidad)
            diaologo_login.set_nombre_usuario(reg.tomar_nombre_de_usuario())
            diaologo_login.contraseña_focus()

    def manejar_registro(self,reg_vista:VistaRegistro, nombre_usuario:str, c1: str, c2:str)->None:
        """ 
        maneja la creacion de cuenta LoginResultado 
        Muestra mensaje en ui y cieera la cista si esta ok."""

        res = self.autentificacion.registro(nombre_usuario,c1,c2)
        if res.ok:
            QMessageBox.information(reg_vista,"OK", res.message)
            reg_vista.accept()
            return
        
        #si hay lista de errores, la mostramos de tallada
        if res.errores:
            QMessageBox.warning(reg_vista,"Error", res.message + "\n"+"\n".join(res.errores))
        else:
            QMessageBox.warning(reg_vista,"Error",res.message)

    def manejar_login(self,login_dialogo:PresentacionLogin, nombre_usuario: str, contraseña:str)->None:
        """
        maneja el login usanfo servicio de autentificacion
        si OK: abre bienvenido y cierra el login"""

        res=self.autentificacion.login(nombre_usuario, contraseña)
        if not res.ok:
            QMessageBox.critical(login_dialogo,"Login invalido",res.message)
            return
        
        #abrimos la pantala de bienvenida
        self.ventana_bienvenido=BienvenidoApp(nombre_usuario)
        self.ventana_bienvenido.show()
    
        login_dialogo.accept()
    
    def abrir_cambiar_contraseña(self,dialogo_login:PresentacionLogin)->None:
        vista=VistaCambiarContraseña()

        vista.set_usuario(dialogo_login.nombre_usuario_input.text())

        vista.activar_cambio=lambda u,a,n1,n2:self.manejar_cambio_contraseña(
            vista,u,a,n1,n2
        )

        vista.exec()

    def manejar_cambio_contraseña(self,vista:VistaCambiarContraseña,nombre_usuario:str,actual:str,nueva1:str,nueva2:str,)->None:
        res = self.autentificacion.cambiar_contraseña(nombre_usuario,actual,nueva1,nueva2)
        if res.ok:
            QMessageBox.information(vista,"OK",res.message)
            vista.accept()
            return
        
        if res.errores:
            QMessageBox.warning(vista,"Error",res.message+"\n"+"\n".join(res.errores))
        else:
            QMessageBox.warning(vista," Error",res.message)