from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QMessageBox,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from datetime import date

from servicios.produccion import ServicioProduccion


class VentanaProduccion(QMainWindow):
    """
    Ventana para sector: Linea de produccion
    - Declara motos (chasis, motor, modelo, color)
    - Muestra tabla con todas las motos
    - Contador diario (solo hoy)
    - Cerrar día: muestra cantidad diaria y cierra app
    """
    def __init__(self, nombre_usuario: str):
        super().__init__()
        self.setWindowTitle(f"Producción - Usuario: {nombre_usuario}")

        self.servicio = ServicioProduccion()

        self._dia_actual = date.today()

        # UI CONTROL
        self.chasis_input = QLineEdit()
        self.chasis_input.setPlaceholderText("Número de chasis")

        self.motor_input = QLineEdit()
        self.motor_input.setPlaceholderText("Número de motor")

        self.modelo_combo = QComboBox()
        self.modelo_combo.addItems(["110", "150"])
        self.modelo_combo.currentTextChanged.connect(self._modelo_cambio)

        self.color_combo = QComboBox()
        self._cargar_colores("110")

        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar por chasis o motor")

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
        self._actualizar_contador()

        # Tabla (tipo treeview simple)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Chasis", "Motor", "Modelo", "Color", "Fecha/Hora"])
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.itemSelectionChanged.connect(self._fila_seleccionada)

        #LAYOUT
        central = QWidget()
        root = QVBoxLayout(central)

        form = QFormLayout()
        form.addRow("Chasis:", self.chasis_input)
        form.addRow("Motor:", self.motor_input)
        form.addRow("Modelo:", self.modelo_combo)
        form.addRow("Color:", self.color_combo)

        acciones1 = QHBoxLayout()
        acciones1.addWidget(self.btn_agregar)
        acciones1.addWidget(self.btn_modificar)
        acciones1.addStretch(1)

        acciones2 = QHBoxLayout()
        acciones2.addWidget(self.buscar_input)
        acciones2.addWidget(self.btn_buscar)
        acciones2.addWidget(self.btn_refrescar)
        acciones2.addStretch(1)
        acciones2.addWidget(self.contador_label)
        acciones2.addWidget(self.btn_cerrar_dia)

        root.addLayout(form)
        root.addLayout(acciones1)
        root.addLayout(acciones2)

        root.addWidget(QLabel("Motos existentes:"))
        root.addWidget(self.tabla)

        self.setCentralWidget(central)

        # cargar inicial
        self._refrescar()

        # timer para detectar cambio de día 
        self.timer = QTimer(self)
        self.timer.setInterval(30_000)  # cada 30s
        self.timer.timeout.connect(self._verificar_cambio_dia)
        self.timer.start()

    # UI METODOS
    def _cargar_colores(self, modelo: str):
        self.color_combo.clear()
        self.color_combo.addItems(self.servicio.colores_para_modelo(modelo))

    def _modelo_cambio(self, modelo: str):
        self._cargar_colores(modelo)

    def _verificar_cambio_dia(self):
        hoy = date.today()
        if hoy != self._dia_actual:
            self._dia_actual = hoy
            self._actualizar_contador()

    def _actualizar_contador(self):
        cantidad = self.servicio.cantidad_del_dia(self._dia_actual)
        self.contador_label.setText(f"Producción de hoy ({self._dia_actual.isoformat()}): {cantidad}")

    def _llenar_tabla(self, motos):
        self.tabla.setRowCount(0)
        for m in motos:
            r = self.tabla.rowCount()
            self.tabla.insertRow(r)

            self.tabla.setItem(r, 0, QTableWidgetItem(m.numero_chasis))
            self.tabla.setItem(r, 1, QTableWidgetItem(m.numero_motor))
            self.tabla.setItem(r, 2, QTableWidgetItem(str(m.modelo)))
            self.tabla.setItem(r, 3, QTableWidgetItem(str(m.color)))
            self.tabla.setItem(r, 4, QTableWidgetItem(m.fecha_hora.strftime("%Y-%m-%d %H:%M:%S")))

        self.tabla.resizeColumnsToContents()

    def _moto_seleccionada_chasis(self) -> str | None:
        items = self.tabla.selectedItems()
        if not items:
            return None
        # columna 0 = chasis
        return items[0].text()

    def _fila_seleccionada(self):
        """
        Cuando seleccionás una fila, precarga los campos (para modificar).
        """
        chasis = self._moto_seleccionada_chasis()
        if not chasis:
            return

        # buscar esa moto en DB 
        motos = self.servicio.buscar(chasis)
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

    #ACCIONES

    def _refrescar(self):
        motos = self.servicio.listar_todas()
        self._llenar_tabla(motos)
        self._actualizar_contador()

    def _buscar_clicked(self):
        texto = self.buscar_input.text()
        motos = self.servicio.buscar(texto)
        self._llenar_tabla(motos)

    def _agregar_clicked(self):
        res = self.servicio.declarar_moto(
            self.chasis_input.text(),
            self.motor_input.text(),
            self.modelo_combo.currentText(),
            self.color_combo.currentText(),
        )

        if res.ok:
            QMessageBox.information(self, "OK", res.message)
            self._refrescar()
            # limpiar inputs
            self.chasis_input.clear()
            self.motor_input.clear()
            self.chasis_input.setFocus()
            return

        if res.errores:
            QMessageBox.warning(self, "Error", res.message + "\n" + "\n".join(res.errores))
        else:
            QMessageBox.warning(self, "Error", res.message)

    def _modificar_clicked(self):
        # chasis lo tomamos del input
        res = self.servicio.modificar_moto_por_chasis(
            self.chasis_input.text(),
            self.motor_input.text(),
            self.modelo_combo.currentText(),
            self.color_combo.currentText(),
        )
        if res.ok:
            QMessageBox.information(self, "OK", res.message)
            self._refrescar()
            return

        if res.errores:
            QMessageBox.warning(self, "Error", res.message + "\n" + "\n".join(res.errores))
        else:
            QMessageBox.warning(self, "Error", res.message)

    def _cerrar_dia_clicked(self):
        cantidad = self.servicio.cantidad_del_dia(self._dia_actual)
        QMessageBox.information(
            self,
            "Cierre de día",
            f"Producción del día ({self._dia_actual.isoformat()}): {cantidad} motos.\n\nEl programa se cerrará."
        )
        self.close()
        # en PyQt cerrar la ultima ventana cierra app