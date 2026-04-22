from __future__ import annotations

from datetime import date

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem, QMessageBox
)

from patrones.observadores import Sujeto, Evento
from servicios.mecanica import ServicioMecanica


class VentanaMecanica(QMainWindow, Sujeto):
    def __init__(self, nombre_usuario: str):
        QMainWindow.__init__(self)
        Sujeto.__init__(self)

        self.setWindowTitle(f"Mecánica - Usuario: {nombre_usuario}")

        self.servicio = ServicioMecanica()
        self._dia_actual = date.today()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(["Chasis", "Motor", "Modelo", "Color", "Fecha/Hora", "Motivo"])
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.clicked.connect(self._refrescar)

        self.btn_dar_alta = QPushButton("Dar alta (volver a Inspección Final)")
        self.btn_dar_alta.clicked.connect(self._dar_alta_clicked)

        self.lbl_resumen = QLabel("")
        self.lbl_resumen.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.btn_cerrar_dia = QPushButton("Cerrar día")
        self.btn_cerrar_dia.clicked.connect(self._cerrar_dia_clicked)

        central = QWidget()
        root = QVBoxLayout(central)

        root.addWidget(QLabel("Motos en Mecánica (A_MECANICA):"))
        root.addWidget(self.tree)

        acciones = QHBoxLayout()
        acciones.addWidget(self.btn_refrescar)
        acciones.addStretch(1)
        acciones.addWidget(self.btn_dar_alta)
        root.addLayout(acciones)

        cierre = QHBoxLayout()
        cierre.addWidget(self.lbl_resumen)
        cierre.addStretch(1)
        cierre.addWidget(self.btn_cerrar_dia)
        root.addLayout(cierre)

        self.setCentralWidget(central)

        self._refrescar()

    def _moto_seleccionada_chasis(self) -> str | None:
        item = self.tree.currentItem()
        if not item:
            return None
        return item.text(0)

    def _actualizar_resumen(self):
        cant = self.servicio.cantidad_reparadas_del_dia(self._dia_actual)
        self.lbl_resumen.setText(f"Reparadas hoy ({self._dia_actual.isoformat()}): {cant}")

    def _refrescar(self):
        self.tree.clear()
        motos = self.servicio.listar_en_mecanica()

        for m in motos:
            it = QTreeWidgetItem([
                m.numero_chasis,
                m.numero_motor,
                str(m.modelo),
                str(m.color),
                m.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                str(m.motivo_rechazo or ""),
            ])
            self.tree.addTopLevelItem(it)

        for i in range(6):
            self.tree.resizeColumnToContents(i)

        self._actualizar_resumen()

    def _dar_alta_clicked(self):
        chasis = self._moto_seleccionada_chasis()
        if not chasis:
            QMessageBox.warning(self, "Error", "Seleccioná una moto.")
            return

        self.notificar(Evento(
            nombre="mecanica_dar_alta",
            data={"chasis": chasis}
        ))

    def _cerrar_dia_clicked(self):
        cant = self.servicio.cantidad_reparadas_del_dia(self._dia_actual)

        QMessageBox.information(
            self,
            "Cierre de día (Mecánica)",
            f"Reparaciones del día ({self._dia_actual.isoformat()}): {cant} motos.\n\nLa ventana se cerrará."
        )

        self.notificar(Evento(
            nombre="mecanica_cierre_dia",
            data={"dia": self._dia_actual.isoformat(), "cantidad": cant}
        ))

        self.close()

    def refrescar(self):
        self._refrescar()