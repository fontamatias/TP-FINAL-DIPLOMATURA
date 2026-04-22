from __future__ import annotations

from datetime import date
from typing import Callable, Iterable

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import QTimer

from patrones.observadores import Sujeto, Evento
from app.constantes import Eventos


class VentanaProduccion(QMainWindow, Sujeto):
    def __init__(self, nombre_usuario: str):
        QMainWindow.__init__(self)
        Sujeto.__init__(self)

        self.setWindowTitle(f"Producción - Usuario: {nombre_usuario}")

        # 4b) Servicio inyectado desde el controlador (la UI no instancia ServicioProduccion)
        self._listar_por_estado: Callable[[str], list] | None = None
        self._buscar_por_estado: Callable[[str, str], list] | None = None
        self._buscar: Callable[[str], list] | None = None
        self._declarar_moto: Callable[[str, str, str, str], Any] | None = None
        self._modificar_moto_por_chasis: Callable[[str, str, str, str], Any] | None = None
        self._colores_para_modelo: Callable[[str], list[str]] | None = None
        self._cantidad_del_dia: Callable[[date], int] | None = None

        self._dia_actual = date.today()

        self.chasis_input = QLineEdit()
        self.chasis_input.setPlaceholderText("Número de chasis")

        self.motor_input = QLineEdit()
        self.motor_input.setPlaceholderText("Número de motor")

        self.modelo_combo = QComboBox()
        self.modelo_combo.addItems(["110", "150"])
        self.modelo_combo.currentTextChanged.connect(self._modelo_cambio)

        self.color_combo = QComboBox()

        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar por chasis o motor")

        # filtro por estado
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["TODOS", "EN_PRODUCCION", "OK_INSPECCION", "A_MECANICA"])
        self.estado_combo.currentTextChanged.connect(lambda _: self._refrescar())

        self.btn_agregar = QPushButton("Agregar moto")
        self.btn_agregar.clicked.connect(self._agregar_clicked)

        self.btn_modificar = QPushButton("Modificar moto seleccionada")
        self.btn_modificar.clicked.connect(self._modificar_clicked)

        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self._buscar_clicked)

        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.clicked.connect(self._refrescar)

        self.btn_cerrar_dia = QPushButton("Cerrar día")
        self.btn_cerrar_dia.clicked.connect(self._cerrar_dia_clicked)

        self.contador_label = QLabel("")
        self.contador_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Chasis", "Motor", "Modelo", "Color", "Fecha/Hora", "Estado"])
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.itemSelectionChanged.connect(self._fila_seleccionada)

        central = QWidget()
        root = QVBoxLayout(central)

        form = QFormLayout()
        form.addRow("Chasis:", self.chasis_input)
        form.addRow("Motor:", self.motor_input)
        form.addRow("Modelo:", self.modelo_combo)
        form.addRow("Color:", self.color_combo)
        root.addLayout(form)

        acciones1 = QHBoxLayout()
        acciones1.addWidget(self.btn_agregar)
        acciones1.addWidget(self.btn_modificar)
        acciones1.addStretch(1)
        root.addLayout(acciones1)

        acciones2 = QHBoxLayout()
        acciones2.addWidget(QLabel("Estado:"))
        acciones2.addWidget(self.estado_combo)
        acciones2.addWidget(self.buscar_input)
        acciones2.addWidget(self.btn_buscar)
        acciones2.addWidget(self.btn_refrescar)
        acciones2.addStretch(1)
        acciones2.addWidget(self.contador_label)
        acciones2.addWidget(self.btn_cerrar_dia)
        root.addLayout(acciones2)

        root.addWidget(QLabel("Motos:"))
        root.addWidget(self.tabla)

        self.setCentralWidget(central)

        self.timer = QTimer(self)
        self.timer.setInterval(30_000)
        self.timer.timeout.connect(self._verificar_cambio_dia)
        self.timer.start()

    # =========================
    # 4b) inyección de servicio
    # =========================
    def set_servicio(
        self,
        *,
        listar_por_estado,
        buscar_por_estado,
        buscar,
        declarar_moto,
        modificar_moto_por_chasis,
        colores_para_modelo,
        cantidad_del_dia,
    ) -> None:
        self._listar_por_estado = listar_por_estado
        self._buscar_por_estado = buscar_por_estado
        self._buscar = buscar
        self._declarar_moto = declarar_moto
        self._modificar_moto_por_chasis = modificar_moto_por_chasis
        self._colores_para_modelo = colores_para_modelo
        self._cantidad_del_dia = cantidad_del_dia

        # inicial
        self._cargar_colores(self.modelo_combo.currentText())
        self._refrescar()
        self._actualizar_contador()

    # --------------------
    # helpers / UI
    # --------------------
    def _cargar_colores(self, modelo: str):
        self.color_combo.clear()
        if not self._colores_para_modelo:
            self.color_combo.addItems([])
            return
        self.color_combo.addItems(self._colores_para_modelo(modelo))

    def _modelo_cambio(self, modelo: str):
        self._cargar_colores(modelo)

    def _verificar_cambio_dia(self):
        hoy = date.today()
        if hoy != self._dia_actual:
            self._dia_actual = hoy
            self._actualizar_contador()

    def _actualizar_contador(self):
        if not self._cantidad_del_dia:
            self.contador_label.setText("")
            return
        cantidad = self._cantidad_del_dia(self._dia_actual)
        self.contador_label.setText(f"Producción de hoy ({self._dia_actual.isoformat()}): {cantidad}")

    def _llenar_tabla(self, motos: Iterable):
        self.tabla.setRowCount(0)
        for m in motos:
            r = self.tabla.rowCount()
            self.tabla.insertRow(r)

            self.tabla.setItem(r, 0, QTableWidgetItem(m.numero_chasis))
            self.tabla.setItem(r, 1, QTableWidgetItem(m.numero_motor))
            self.tabla.setItem(r, 2, QTableWidgetItem(str(m.modelo)))
            self.tabla.setItem(r, 3, QTableWidgetItem(str(m.color)))
            self.tabla.setItem(r, 4, QTableWidgetItem(m.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")))
            self.tabla.setItem(r, 5, QTableWidgetItem(str(getattr(m, "estado", ""))))

        self.tabla.resizeColumnsToContents()

    def _moto_seleccionada_chasis(self) -> str | None:
        items = self.tabla.selectedItems()
        if not items:
            return None
        return items[0].text()

    def _fila_seleccionada(self):
        chasis = self._moto_seleccionada_chasis()
        if not chasis or not self._buscar:
            return

        motos = self._buscar(chasis)
        if not motos:
            return

        m = motos[0]
        self.chasis_input.setText(m.numero_chasis)
        self.motor_input.setText(m.numero_motor)

        idx_modelo = self.modelo_combo.findText(str(m.modelo))
        if idx_modelo >= 0:
            self.modelo_combo.setCurrentIndex(idx_modelo)

        idx_color = self.color_combo.findText(str(m.color))
        if idx_color >= 0:
            self.color_combo.setCurrentIndex(idx_color)

    def _refrescar(self):
        if not self._listar_por_estado:
            return
        estado = self.estado_combo.currentText().strip()
        motos = self._listar_por_estado(estado)
        self._llenar_tabla(motos)
        self._actualizar_contador()

    def _buscar_clicked(self):
        if not self._buscar_por_estado:
            return
        texto = self.buscar_input.text()
        estado = self.estado_combo.currentText().strip()
        motos = self._buscar_por_estado(texto, estado)
        self._llenar_tabla(motos)

    def _agregar_clicked(self):
        if not self._declarar_moto:
            return
        res = self._declarar_moto(
            self.chasis_input.text(),
            self.motor_input.text(),
            self.modelo_combo.currentText(),
            self.color_combo.currentText(),
        )

        if getattr(res, "ok", False):
            QMessageBox.information(self, "OK", getattr(res, "message", "Moto agregada."))
            self._refrescar()
            self.chasis_input.clear()
            self.motor_input.clear()
            self.chasis_input.setFocus()
            return

        errores = getattr(res, "errores", None)
        msg = getattr(res, "message", "Error.")
        if errores:
            msg = msg + "\n" + "\n".join(errores)
        QMessageBox.warning(self, "Error", msg)

    def _modificar_clicked(self):
        if not self._modificar_moto_por_chasis:
            return
        res = self._modificar_moto_por_chasis(
            self.chasis_input.text(),
            self.motor_input.text(),
            self.modelo_combo.currentText(),
            self.color_combo.currentText(),
        )
        if getattr(res, "ok", False):
            QMessageBox.information(self, "OK", getattr(res, "message", "Moto modificada."))
            self._refrescar()
            return

        errores = getattr(res, "errores", None)
        msg = getattr(res, "message", "Error.")
        if errores:
            msg = msg + "\n" + "\n".join(errores)
        QMessageBox.warning(self, "Error", msg)

    def _cerrar_dia_clicked(self):
        cantidad = self._cantidad_del_dia(self._dia_actual) if self._cantidad_del_dia else 0
        QMessageBox.information(
            self,
            "Cierre de día",
            f"Producción del día ({self._dia_actual.isoformat()}): {cantidad} motos.\n\nEl programa se cerrará."
        )

        self.notificar(Evento(
            nombre=Eventos.PRODUCCION_CIERRE_DIA,
            data={"dia": self._dia_actual.isoformat(), "cantidad": cantidad}
        ))

        self.close()