from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

from patrones.observadores import Sujeto, Evento
from servicios.inspeccion_final import ServicioInspeccionFinal, MOTIVOS_NO_OK


class VentanaInspeccionFinal(QMainWindow, Sujeto):
    def __init__(self, nombre_usuario: str):
        QMainWindow.__init__(self)
        Sujeto.__init__(self)

        self.setWindowTitle(f"Inspección final - Usuario: {nombre_usuario}")

        self.servicio = ServicioInspeccionFinal()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(["Chasis", "Motor", "Modelo", "Color", "Fecha/Hora"])
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

        self.motivo_combo = QComboBox()
        self.motivo_combo.addItem("")  # vacío para obligar a elegir
        self.motivo_combo.addItems(MOTIVOS_NO_OK)

        self.lbl_motivo = QLabel("Motivo (si NO OK):")
        self.lbl_motivo.setStyleSheet("font-weight:bold;")

        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.clicked.connect(self._refrescar)

        self.btn_ok = QPushButton("Marcar OK")
        self.btn_ok.clicked.connect(self._ok_clicked)

        self.btn_no_ok = QPushButton("Marcar NO OK (a Mecánica)")
        self.btn_no_ok.clicked.connect(self._no_ok_clicked)

        # Layout
        central = QWidget()
        root = QVBoxLayout(central)

        root.addWidget(QLabel("Motos pendientes de inspección (EN_PRODUCCION):"))
        root.addWidget(self.tree)

        acciones = QHBoxLayout()
        acciones.addWidget(self.btn_refrescar)
        acciones.addStretch(1)
        acciones.addWidget(self.btn_ok)
        root.addLayout(acciones)

        no_ok_layout = QHBoxLayout()
        no_ok_layout.addWidget(self.lbl_motivo)
        no_ok_layout.addWidget(self.motivo_combo)
        no_ok_layout.addStretch(1)
        no_ok_layout.addWidget(self.btn_no_ok)
        root.addLayout(no_ok_layout)

        self.setCentralWidget(central)

        self._refrescar()

    def _moto_seleccionada_chasis(self) -> str | None:
        item = self.tree.currentItem()
        if not item:
            return None
        return item.text(0)

    def _refrescar(self):
        self.tree.clear()
        motos = self.servicio.listar_pendientes()

        for m in motos:
            it = QTreeWidgetItem([
                m.numero_chasis,
                m.numero_motor,
                str(m.modelo),
                str(m.color),
                m.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
            ])
            self.tree.addTopLevelItem(it)

        self.tree.resizeColumnToContents(0)
        self.tree.resizeColumnToContents(1)
        self.tree.resizeColumnToContents(2)
        self.tree.resizeColumnToContents(3)

    def _ok_clicked(self):
        chasis = self._moto_seleccionada_chasis()
        if not chasis:
            QMessageBox.warning(self, "Error", "Seleccioná una moto.")
            return

        # emitimos evento -> controlador decide (patrón observador)
        self.notificar(Evento(
            nombre="inspeccion_marcar_ok",
            data={"chasis": chasis}
        ))

    def _no_ok_clicked(self):
        chasis = self._moto_seleccionada_chasis()
        if not chasis:
            QMessageBox.warning(self, "Error", "Seleccioná una moto.")
            return

        motivo = self.motivo_combo.currentText().strip()
        if not motivo:
            QMessageBox.warning(self, "Error", "Seleccioná un motivo en el desplegable.")
            return

        self.notificar(Evento(
            nombre="inspeccion_marcar_no_ok",
            data={"chasis": chasis, "motivo": motivo}
        ))

    # helpers para controlador
    def refrescar(self):
        self._refrescar()