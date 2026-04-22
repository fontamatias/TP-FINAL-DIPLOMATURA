from __future__ import annotations

from datetime import date

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QComboBox, QMessageBox
)

from patrones.observadores import Sujeto, Evento
from servicios.inspeccion_final import ServicioInspeccionFinal, MOTIVOS_NO_OK


class VentanaInspeccionFinal(QMainWindow, Sujeto):
    def __init__(self, nombre_usuario: str):
        QMainWindow.__init__(self)
        Sujeto.__init__(self)

        self.setWindowTitle(f"Inspección final - Usuario: {nombre_usuario}")

        self.servicio = ServicioInspeccionFinal()
        self._dia_actual = date.today()

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

        # NUEVO: resumen + cerrar día
        self.lbl_resumen = QLabel("")
        self.lbl_resumen.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.btn_cerrar_dia = QPushButton("Cerrar día")
        self.btn_cerrar_dia.clicked.connect(self._cerrar_dia_clicked)

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

        cierre_layout = QHBoxLayout()
        cierre_layout.addWidget(self.lbl_resumen)
        cierre_layout.addStretch(1)
        cierre_layout.addWidget(self.btn_cerrar_dia)
        root.addLayout(cierre_layout)

        self.setCentralWidget(central)

        self._refrescar()

    def _moto_seleccionada_chasis(self) -> str | None:
        item = self.tree.currentItem()
        if not item:
            return None
        return item.text(0)

    def _actualizar_resumen(self):
        ok_hoy = self.servicio.cantidad_ok_del_dia(self._dia_actual)
        no_ok_hoy = self.servicio.cantidad_no_ok_del_dia(self._dia_actual)
        self.lbl_resumen.setText(
            f"Inspección de hoy ({self._dia_actual.isoformat()}): OK={ok_hoy} | NO OK={no_ok_hoy}"
        )

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

        self._actualizar_resumen()

    def _ok_clicked(self):
        chasis = self._moto_seleccionada_chasis()
        if not chasis:
            QMessageBox.warning(self, "Error", "Seleccioná una moto.")
            return

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

    def _cerrar_dia_clicked(self):
        ok_hoy = self.servicio.cantidad_ok_del_dia(self._dia_actual)
        no_ok_hoy = self.servicio.cantidad_no_ok_del_dia(self._dia_actual)

        QMessageBox.information(
            self,
            "Cierre de día (Inspección Final)",
            f"Inspección del día ({self._dia_actual.isoformat()}):\n\n"
            f"OK: {ok_hoy}\n"
            f"NO OK: {no_ok_hoy}\n\n"
            "La ventana se cerrará."
        )

        self.notificar(Evento(
            nombre="inspeccion_cierre_dia",
            data={"dia": self._dia_actual.isoformat(), "ok": ok_hoy, "no_ok": no_ok_hoy}
        ))

        self.close()

    # helper para controlador
    def refrescar(self):
        self._refrescar()