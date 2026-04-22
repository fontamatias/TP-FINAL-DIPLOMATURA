"""
controlador/app_controlador.py
-----------------------------
controlador principal usando patron Observador:
- las vistas emiten eventos
- el controlador escucha y actua
"""
from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox

from patrones.observadores import Observador, Evento

from servicios.autentificacion import ServicioAutentificacion
from servicios.inspeccion_final import ServicioInspeccionFinal
from servicios.mecanica import ServicioMecanica
from servicios.distribucion import ServicioDistribucion

from ui.loginUi import PresentacionLogin
from ui.registroUi import VistaRegistro
from ui.Bienvenida import BienvenidoApp
from ui.cambiarCC import VistaCambiarContraseña
from ui.eliminarUsuario import VistaEliminarUsuario
from ui.produccionUi import VentanaProduccion
from ui.inspeccionFinalUi import VentanaInspeccionFinal
from ui.mecanicaUi import VentanaMecanica
from ui.distribucionUi import VentanaDistribucion

from modelo.empleados import Usuario


class ControladorDeApp(Observador):
    def __init__(self):
        self.autentificacion = ServicioAutentificacion()
        self.inspeccion_srv = ServicioInspeccionFinal()
        self.mecanica_srv = ServicioMecanica()
        self.distribucion_srv = ServicioDistribucion()

        self.login: PresentacionLogin | None = None
        self.ventana_bienvenido = None
        self._registro: VistaRegistro | None = None
        self._cambiar: VistaCambiarContraseña | None = None
        self._eliminar: VistaEliminarUsuario | None = None
        self._produccion: VentanaProduccion | None = None
        self._inspeccion: VentanaInspeccionFinal | None = None
        self._mecanica: VentanaMecanica | None = None
        self._distribucion: VentanaDistribucion | None = None

    def arranque(self) -> int:
        self.login = PresentacionLogin()
        self.login.conectar(self)

        resultado = self.login.exec()
        if resultado == PresentacionLogin.DialogCode.Accepted:
            return 1
        return 0

    # OBSERVADOR
    def update(self, subject, evento: Evento) -> None:
        nombre = evento.nombre
        data = evento.data or {}

        # eventos del login
        if nombre == "login_submit":
            self._manejar_login(subject, data)
            return

        if nombre == "registro_requested":
            self._abrir_registro(subject)
            return

        if nombre == "cambiar_contrasena_requested":
            self._abrir_cambiar_contrasena(subject)
            return

        if nombre == "eliminar_usuario_requested":
            self._abrir_eliminar_usuario(subject)
            return

        # eventos del registro
        if nombre == "registro_submit":
            self._manejar_registro(subject, data)
            return

        # eventos cambiar contraseña
        if nombre == "cambiar_contrasena_submit":
            self._manejar_cambio_contrasena(subject, data)
            return

        # eventos eliminar usuario
        if nombre == "eliminar_usuario_submit":
            self._manejar_eliminar_usuario(subject, data)
            return

        # eventos inspeccion final
        if nombre == "inspeccion_marcar_ok":
            self._manejar_inspeccion_ok(subject, data)
            return

        if nombre == "inspeccion_marcar_no_ok":
            self._manejar_inspeccion_no_ok(subject, data)
            return

        if nombre == "inspeccion_cierre_dia":
            return

        # eventos mecánica
        if nombre == "mecanica_dar_alta":
            self._manejar_mecanica_dar_alta(subject, data)
            return

        if nombre == "mecanica_cierre_dia":
            return

        # eventos distribución
        if nombre == "distribucion_crear_pedido":
            self._manejar_distribucion_crear_pedido(subject)
            return

        if nombre == "distribucion_agregar_a_pedido":
            self._manejar_distribucion_agregar_a_pedido(subject, data)
            return

        if nombre == "distribucion_finalizar_pedido":
            self._manejar_distribucion_finalizar_pedido(subject, data)
            return

        if nombre == "distribucion_cierre_dia":
            return

        # eventos produccion
        if nombre == "produccion_cierre_dia":
            return

        print(f"Evento no manejado: {evento}")

    # ---- acciones ----
    def _abrir_registro(self, dialogo_login: PresentacionLogin) -> None:
        reg = VistaRegistro()
        reg.conectar(self)
        self._registro = reg

        if reg.exec() == VistaRegistro.DialogCode.Accepted:
            dialogo_login.set_nombre_usuario(reg.tomar_nombre_de_usuario())
            dialogo_login.contraseña_focus()

        reg.desconectar(self)
        self._registro = None

    def _manejar_registro(self, reg_vista: VistaRegistro, data: dict) -> None:
        u = data.get("usuario", "")
        c1 = data.get("c1", "")
        c2 = data.get("c2", "")
        sector = data.get("sector", "")

        res = self.autentificacion.registro(u, c1, c2, sector)
        if res.ok:
            QMessageBox.information(reg_vista, "OK", res.message)
            reg_vista.accept()
            return

        if res.errores:
            QMessageBox.warning(reg_vista, "Error", res.message + "\n" + "\n".join(res.errores))
        else:
            QMessageBox.warning(reg_vista, "Error", res.message)

    def _manejar_login(self, login_dialogo: PresentacionLogin, data: dict) -> None:
        nombre_usuario = data.get("usuario", "")
        contraseña = data.get("contraseña", "")

        res = self.autentificacion.login(nombre_usuario, contraseña)
        if not res.ok:
            QMessageBox.critical(login_dialogo, "Login invalido", res.message)
            return

        usuario = Usuario.get_or_none(Usuario.nombre_usuario == (nombre_usuario or "").strip())
        sector = usuario.sector if usuario else ""

        if sector == "Linea de produccion":
            prod = VentanaProduccion(nombre_usuario)
            prod.conectar(self)
            self._produccion = prod
            prod.show()
            login_dialogo.accept()
            return

        if sector == "Inspeccion final":
            insp = VentanaInspeccionFinal(nombre_usuario)
            insp.conectar(self)
            self._inspeccion = insp
            insp.show()
            login_dialogo.accept()
            return

        if sector == "Mecanica":
            mec = VentanaMecanica(nombre_usuario)
            mec.conectar(self)
            self._mecanica = mec
            mec.show()
            login_dialogo.accept()
            return

        if sector == "Distribucion":
            dist = VentanaDistribucion(nombre_usuario)
            dist.conectar(self)
            self._distribucion = dist
            dist.show()
            login_dialogo.accept()
            return

        bien = BienvenidoApp(nombre_usuario, sector)
        self.ventana_bienvenido = bien
        bien.show()
        login_dialogo.accept()

    def _abrir_cambiar_contrasena(self, dialogo_login: PresentacionLogin) -> None:
        vista = VistaCambiarContraseña()
        vista.conectar(self)
        self._cambiar = vista

        vista.set_usuario(dialogo_login.nombre_usuario_input.text())
        vista.exec()

        vista.desconectar(self)
        self._cambiar = None

    def _manejar_cambio_contrasena(self, vista: VistaCambiarContraseña, data: dict) -> None:
        u = data.get("usuario", "")
        actual = data.get("actual", "")
        n1 = data.get("nueva1", "")
        n2 = data.get("nueva2", "")

        res = self.autentificacion.cambiar_contrasena(u, actual, n1, n2)
        if res.ok:
            QMessageBox.information(vista, "OK", res.message)
            vista.accept()
            return

        if res.errores:
            QMessageBox.warning(vista, "Error", res.message + "\n" + "\n".join(res.errores))
        else:
            QMessageBox.warning(vista, "Error", res.message)

    def _abrir_eliminar_usuario(self, dialogo_login: PresentacionLogin) -> None:
        vista = VistaEliminarUsuario()
        vista.conectar(self)
        self._eliminar = vista

        vista.set_usuario(dialogo_login.nombre_usuario_input.text())
        vista.exec()

        vista.desconectar(self)
        self._eliminar = None

    def _manejar_eliminar_usuario(self, vista: VistaEliminarUsuario, data: dict) -> None:
        u = data.get("usuario", "")
        actual = data.get("actual", "")

        res = self.autentificacion.eliminar_usuario(u, actual)
        if res.ok:
            QMessageBox.information(vista, "OK", res.message)
            vista.accept()
            return

        QMessageBox.warning(vista, "Error", res.message)

    # ============================
    # handlers Inspecci��n Final
    # ============================
    def _manejar_inspeccion_ok(self, vista: VentanaInspeccionFinal, data: dict) -> None:
        chasis = data.get("chasis", "")
        res = self.inspeccion_srv.marcar_ok(chasis)

        if res.ok:
            QMessageBox.information(vista, "OK", res.message)
            vista.refrescar()
            return

        QMessageBox.warning(vista, "Error", res.message)

    def _manejar_inspeccion_no_ok(self, vista: VentanaInspeccionFinal, data: dict) -> None:
        chasis = data.get("chasis", "")
        motivo = data.get("motivo", "")
        res = self.inspeccion_srv.marcar_no_ok(chasis, motivo)

        if res.ok:
            QMessageBox.information(vista, "OK", res.message)
            vista.refrescar()
            return

        if getattr(res, "errores", None):
            QMessageBox.warning(vista, "Error", res.message + "\n" + "\n".join(res.errores or []))
        else:
            QMessageBox.warning(vista, "Error", res.message)

    # ============================
    # handlers Mecánica
    # ============================
    def _manejar_mecanica_dar_alta(self, vista: VentanaMecanica, data: dict) -> None:
        chasis = data.get("chasis", "")
        res = self.mecanica_srv.dar_alta(chasis)

        if res.ok:
            QMessageBox.information(vista, "OK", res.message)
            vista.refrescar()
            return

        QMessageBox.warning(vista, "Error", res.message)

    # ============================
    # handlers Distribución
    # ============================
    def _manejar_distribucion_crear_pedido(self, vista: VentanaDistribucion) -> None:
        venta = self.distribucion_srv.crear_venta_pendiente()
        QMessageBox.information(vista, "OK", f"Pedido creado. Nro de venta: {venta.numero_venta}")
        vista.set_pedido_actual(venta.id, venta.numero_venta)
        vista.refrescar()

    def _manejar_distribucion_agregar_a_pedido(self, vista: VentanaDistribucion, data: dict) -> None:
        venta_id = data.get("venta_id")
        chasis = data.get("chasis", "")

        try:
            venta_id_int = int(venta_id)
        except Exception:
            QMessageBox.warning(vista, "Error", "Venta inválida.")
            return

        res = self.distribucion_srv.agregar_moto_a_venta(venta_id_int, chasis)
        if res.ok:
            QMessageBox.information(vista, "OK", res.message)
            vista.refrescar()
        else:
            QMessageBox.warning(vista, "Error", res.message)

    def _manejar_distribucion_finalizar_pedido(self, vista: VentanaDistribucion, data: dict) -> None:
        venta_id = data.get("venta_id")
        try:
            venta_id_int = int(venta_id)
        except Exception:
            QMessageBox.warning(vista, "Error", "Venta inválida.")
            return

        res = self.distribucion_srv.finalizar_venta(venta_id_int)
        if res.ok:
            QMessageBox.information(vista, "OK", res.message)
            vista.set_pedido_actual(None, None)
            vista.refrescar()
        else:
            QMessageBox.warning(vista, "Error", res.message)