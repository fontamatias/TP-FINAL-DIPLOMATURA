"""
controlador/app_controlador.py
-----------------------------
controlador principal usando patron Observador:
- las vistas emiten eventos
- el controlador escucha y actua
"""
from __future__ import annotations

from typing import Any, Callable

from PyQt6.QtWidgets import QMessageBox

from patrones.observadores import Observador, Evento

from app.constantes import Eventos, Sectores

from servicios.autentificacion import ServicioAutentificacion
from servicios.inspeccion_final import ServicioInspeccionFinal
from servicios.mecanica import ServicioMecanica
from servicios.distribucion import ServicioDistribucion
from servicios.produccion import ServicioProduccion

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
        # servicios (única fuente)
        self.autentificacion = ServicioAutentificacion()
        self.produccion_srv = ServicioProduccion()
        self.inspeccion_srv = ServicioInspeccionFinal()
        self.mecanica_srv = ServicioMecanica()
        self.distribucion_srv = ServicioDistribucion()

        # vistas activas
        self.login: PresentacionLogin | None = None
        self.ventana_bienvenido = None
        self._registro: VistaRegistro | None = None
        self._cambiar: VistaCambiarContraseña | None = None
        self._eliminar: VistaEliminarUsuario | None = None
        self._produccion: VentanaProduccion | None = None
        self._inspeccion: VentanaInspeccionFinal | None = None
        self._mecanica: VentanaMecanica | None = None
        self._distribucion: VentanaDistribucion | None = None

        # 4a) dispatcher
        self._handlers: dict[str, Callable[[Any, dict], None]] = {
            # login/auth
            Eventos.LOGIN_SUBMIT: self._h_login_submit,
            Eventos.REGISTRO_REQUESTED: self._h_registro_requested,
            Eventos.CAMBIAR_CONTRASENA_REQUESTED: self._h_cambiar_contrasena_requested,
            Eventos.ELIMINAR_USUARIO_REQUESTED: self._h_eliminar_usuario_requested,
            Eventos.REGISTRO_SUBMIT: self._h_registro_submit,
            Eventos.CAMBIAR_CONTRASENA_SUBMIT: self._h_cambiar_contrasena_submit,
            Eventos.ELIMINAR_USUARIO_SUBMIT: self._h_eliminar_usuario_submit,
            # inspección final
            Eventos.INSPECCION_MARCAR_OK: self._h_inspeccion_ok,
            Eventos.INSPECCION_MARCAR_NO_OK: self._h_inspeccion_no_ok,
            Eventos.INSPECCION_CIERRE_DIA: self._h_inspeccion_cierre_dia,
            # mecánica
            Eventos.MECANICA_DAR_ALTA: self._h_mecanica_dar_alta,
            Eventos.MECANICA_CIERRE_DIA: self._h_mecanica_cierre_dia,
            # distribución
            Eventos.DISTRIBUCION_CREAR_PEDIDO: self._h_distribucion_crear_pedido,
            Eventos.DISTRIBUCION_AGREGAR_A_PEDIDO: self._h_distribucion_agregar_a_pedido,
            Eventos.DISTRIBUCION_FINALIZAR_PEDIDO: self._h_distribucion_finalizar_pedido,
            Eventos.DISTRIBUCION_CIERRE_DIA: self._h_distribucion_cierre_dia,
            # producción
            Eventos.PRODUCCION_CIERRE_DIA: self._h_produccion_cierre_dia,
        }

    def arranque(self) -> int:
        self.login = PresentacionLogin()
        self.login.conectar(self)

        resultado = self.login.exec()
        if resultado == PresentacionLogin.DialogCode.Accepted:
            return 1
        return 0

    # ============================
    # 4d) helpers de mensajes
    # ============================
    def _msg_ok(self, parent, titulo: str, mensaje: str) -> None:
        QMessageBox.information(parent, titulo, mensaje)

    def _msg_warn(self, parent, titulo: str, mensaje: str) -> None:
        QMessageBox.warning(parent, titulo, mensaje)

    def _msg_crit(self, parent, titulo: str, mensaje: str) -> None:
        QMessageBox.critical(parent, titulo, mensaje)

    def _mostrar_resultado(self, parent, res, ok_title="OK", err_title="Error", refresh: Callable[[], None] | None = None):
        """
        res: objeto con atributos ok, message y opcional errores
        """
        if getattr(res, "ok", False):
            self._msg_ok(parent, ok_title, getattr(res, "message", "Operación exitosa."))
            if refresh:
                refresh()
            return True

        msg = getattr(res, "message", "Ocurrió un error.")
        errores = getattr(res, "errores", None)
        if errores:
            msg = msg + "\n" + "\n".join(errores)
        self._msg_warn(parent, err_title, msg)
        return False

    # ============================
    # OBSERVADOR
    # ============================
    def update(self, subject, evento: Evento) -> None:
        nombre = evento.nombre
        data = evento.data or {}

        handler = self._handlers.get(nombre)
        if not handler:
            print(f"Evento no manejado: {evento}")
            return

        handler(subject, data)

    # ============================
    # handlers login/auth
    # ============================
    def _h_registro_requested(self, dialogo_login: PresentacionLogin, data: dict) -> None:
        reg = VistaRegistro()
        reg.conectar(self)
        self._registro = reg

        if reg.exec() == VistaRegistro.DialogCode.Accepted:
            dialogo_login.set_nombre_usuario(reg.tomar_nombre_de_usuario())
            dialogo_login.contraseña_focus()

        reg.desconectar(self)
        self._registro = None

    def _h_registro_submit(self, reg_vista: VistaRegistro, data: dict) -> None:
        u = data.get("usuario", "")
        c1 = data.get("c1", "")
        c2 = data.get("c2", "")
        sector = data.get("sector", "")

        res = self.autentificacion.registro(u, c1, c2, sector)
        if self._mostrar_resultado(reg_vista, res):
            reg_vista.accept()

    def _h_login_submit(self, login_dialogo: PresentacionLogin, data: dict) -> None:
        nombre_usuario = data.get("usuario", "")
        contrasena = data.get("contraseña", "")

        res = self.autentificacion.login(nombre_usuario, contrasena)
        if not getattr(res, "ok", False):
            self._msg_crit(login_dialogo, "Login inválido", getattr(res, "message", "Login inválido."))
            return

        usuario = Usuario.get_or_none(Usuario.nombre_usuario == (nombre_usuario or "").strip())
        sector = usuario.sector if usuario else ""

        # 4b) inyección: las vistas NO crean servicios; el controlador les setea callbacks
        if sector == Sectores.LINEA_PRODUCCION:
            prod = VentanaProduccion(nombre_usuario)
            prod.conectar(self)
            self._produccion = prod

            prod.set_servicio(
                listar_por_estado=self.produccion_srv.listar_por_estado,
                buscar_por_estado=self.produccion_srv.buscar_por_estado,
                buscar=self.produccion_srv.buscar,
                declarar_moto=self.produccion_srv.declarar_moto,
                modificar_moto_por_chasis=self.produccion_srv.modificar_moto_por_chasis,
                colores_para_modelo=self.produccion_srv.colores_para_modelo,
                cantidad_del_dia=self.produccion_srv.cantidad_del_dia,
            )

            prod.show()
            login_dialogo.accept()
            return

        if sector == Sectores.INSPECCION_FINAL:
            insp = VentanaInspeccionFinal(nombre_usuario)
            insp.conectar(self)
            self._inspeccion = insp

            insp.set_servicio(
                listar_pendientes=self.inspeccion_srv.listar_pendientes,
                cantidad_ok_del_dia=self.inspeccion_srv.cantidad_ok_del_dia,
                cantidad_no_ok_del_dia=self.inspeccion_srv.cantidad_no_ok_del_dia,
            )

            insp.show()
            login_dialogo.accept()
            return

        if sector == Sectores.MECANICA:
            mec = VentanaMecanica(nombre_usuario)
            mec.conectar(self)
            self._mecanica = mec

            mec.set_servicio(
                listar_en_mecanica=self.mecanica_srv.listar_en_mecanica,
                cantidad_reparadas_del_dia=self.mecanica_srv.cantidad_reparadas_del_dia,
            )

            mec.show()
            login_dialogo.accept()
            return

        if sector == Sectores.DISTRIBUCION:
            dist = VentanaDistribucion(nombre_usuario)
            dist.conectar(self)
            self._distribucion = dist

            dist.set_servicio(
                listar_stock_listo=self.distribucion_srv.listar_stock_listo,
                listar_ventas_pendientes=self.distribucion_srv.listar_ventas_pendientes,
                listar_ventas_finalizadas=self.distribucion_srv.listar_ventas_finalizadas,
                items_de_venta=self.distribucion_srv.items_de_venta,
                ventas_finalizadas_del_dia=self.distribucion_srv.ventas_finalizadas_del_dia,
                motos_vendidas_del_dia=self.distribucion_srv.motos_vendidas_del_dia,
            )

            dist.show()
            login_dialogo.accept()
            return

        bien = BienvenidoApp(nombre_usuario, sector)
        self.ventana_bienvenido = bien
        bien.show()
        login_dialogo.accept()

    def _h_cambiar_contrasena_requested(self, dialogo_login: PresentacionLogin, data: dict) -> None:
        vista = VistaCambiarContraseña()
        vista.conectar(self)
        self._cambiar = vista

        vista.set_usuario(dialogo_login.nombre_usuario_input.text())
        vista.exec()

        vista.desconectar(self)
        self._cambiar = None

    def _h_cambiar_contrasena_submit(self, vista: VistaCambiarContraseña, data: dict) -> None:
        u = data.get("usuario", "")
        actual = data.get("actual", "")
        n1 = data.get("nueva1", "")
        n2 = data.get("nueva2", "")

        res = self.autentificacion.cambiar_contrasena(u, actual, n1, n2)
        if self._mostrar_resultado(vista, res):
            vista.accept()

    def _h_eliminar_usuario_requested(self, dialogo_login: PresentacionLogin, data: dict) -> None:
        vista = VistaEliminarUsuario()
        vista.conectar(self)
        self._eliminar = vista

        vista.set_usuario(dialogo_login.nombre_usuario_input.text())
        vista.exec()

        vista.desconectar(self)
        self._eliminar = None

    def _h_eliminar_usuario_submit(self, vista: VistaEliminarUsuario, data: dict) -> None:
        u = data.get("usuario", "")
        actual = data.get("actual", "")

        res = self.autentificacion.eliminar_usuario(u, actual)
        if getattr(res, "ok", False):
            self._msg_ok(vista, "OK", getattr(res, "message", "Usuario eliminado."))
            vista.accept()
            return
        self._msg_warn(vista, "Error", getattr(res, "message", "No se pudo eliminar el usuario."))

    # ============================
    # handlers Inspección Final
    # ============================
    def _h_inspeccion_ok(self, vista: VentanaInspeccionFinal, data: dict) -> None:
        chasis = data.get("chasis", "")
        res = self.inspeccion_srv.marcar_ok(chasis)
        self._mostrar_resultado(vista, res, refresh=vista.refrescar)

    def _h_inspeccion_no_ok(self, vista: VentanaInspeccionFinal, data: dict) -> None:
        chasis = data.get("chasis", "")
        motivo = data.get("motivo", "")
        res = self.inspeccion_srv.marcar_no_ok(chasis, motivo)
        self._mostrar_resultado(vista, res, refresh=vista.refrescar)

    def _h_inspeccion_cierre_dia(self, vista: VentanaInspeccionFinal, data: dict) -> None:
        # 4c) cierre de día “real”: acá podrías persistir auditoría si querés.
        # Por ahora, dejamos consistente: se cierra la ventana (ya se cerró en UI)
        # y liberamos referencia.
        self._inspeccion = None

    # ============================
    # handlers Mecánica
    # ============================
    def _h_mecanica_dar_alta(self, vista: VentanaMecanica, data: dict) -> None:
        chasis = data.get("chasis", "")
        res = self.mecanica_srv.dar_alta(chasis)
        self._mostrar_resultado(vista, res, refresh=vista.refrescar)

    def _h_mecanica_cierre_dia(self, vista: VentanaMecanica, data: dict) -> None:
        self._mecanica = None

    # ============================
    # handlers Distribución
    # ============================
    def _h_distribucion_crear_pedido(self, vista: VentanaDistribucion, data: dict) -> None:
        venta = self.distribucion_srv.crear_venta_pendiente()
        self._msg_ok(vista, "OK", f"Pedido creado. Nro de venta: {venta.numero_venta}")
        vista.set_pedido_actual(venta.id, venta.numero_venta)
        vista.refrescar()

    def _h_distribucion_agregar_a_pedido(self, vista: VentanaDistribucion, data: dict) -> None:
        venta_id = data.get("venta_id")
        chasis = data.get("chasis", "")

        try:
            venta_id_int = int(venta_id)
        except Exception:
            self._msg_warn(vista, "Error", "Venta inválida.")
            return

        res = self.distribucion_srv.agregar_moto_a_venta(venta_id_int, chasis)
        self._mostrar_resultado(vista, res, refresh=vista.refrescar)

    def _h_distribucion_finalizar_pedido(self, vista: VentanaDistribucion, data: dict) -> None:
        venta_id = data.get("venta_id")
        try:
            venta_id_int = int(venta_id)
        except Exception:
            self._msg_warn(vista, "Error", "Venta inválida.")
            return

        res = self.distribucion_srv.finalizar_venta(venta_id_int)
        if getattr(res, "ok", False):
            self._msg_ok(vista, "OK", getattr(res, "message", "Pedido finalizado."))
            vista.set_pedido_actual(None, None)
            vista.refrescar()
            return

        self._msg_warn(vista, "Error", getattr(res, "message", "No se pudo finalizar el pedido."))

    def _h_distribucion_cierre_dia(self, vista: VentanaDistribucion, data: dict) -> None:
        self._distribucion = None

    # ============================
    # handlers Producción
    # ============================
    def _h_produccion_cierre_dia(self, vista: VentanaProduccion, data: dict) -> None:
        self._produccion = None