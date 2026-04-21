"""
ui/inspeccionFinalUi.py
-----------------------
Ventana de Inspección Final: muestra todas las motos en un QTreeView
y permite marcarlas OK o NO OK con motivo.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTreeView, QHeaderView,
    QDialog, QDialogButtonBox, QComboBox, QFormLayout,
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt

from servicios.inspeccion_final import ServicioInspeccionFinal, MOTIVOS_NO_OK
from patrones.observadores import Sujeto, Evento


# ──────────────────────────────────────────────
# Diálogo modal para elegir motivo de NO OK
# ──────────────────────────────────────────────
class DialogoMotivoNoOk(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Motivo - NO OK")
        self.setModal(True)
        self.setFixedSize(360, 150)

        self.combo = QComboBox()
        self.combo.addItems(MOTIVOS_NO_OK)

        form = QFormLayout()
        form.addRow("Motivo:", self.combo)

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(botones)

    def motivo_seleccionado(self) -> str:
        return self.combo.currentText()


# ──────────────────────────────────────────────
# Ventana principal de Inspección Final
# ──────────────────────────────────────────────
class VentanaInspeccionFinal(QMainWindow, Sujeto):
    _COLS = ["Chasis", "Motor", "Modelo", "Color", "Fecha/Hora", "Estado", "Motivo"]

    _COLORES_ESTADO = {
        "OK": QColor("#008000"),
        "NO_OK": QColor("#c80000"),
        "PENDIENTE": QColor("#b48200"),
    }

    def __init__(self, nombre_usuario: str):
        QMainWindow.__init__(self)
        Sujeto.__init__(self)

        self.setWindowTitle(f"Inspección Final - Usuario: {nombre_usuario}")
        self.resize(960, 560)

        self.servicio = ServicioInspeccionFinal()

        # ── TreeView ──
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(self._COLS)

        self.tree = QTreeView()
        self.tree.setModel(self.tree_model)
        self.tree.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.tree.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tree.selectionModel().selectionChanged.connect(self._seleccion_cambiada)

        # ── Botones ──
        self.btn_ok = QPushButton("✔  Marcar OK")
        self.btn_ok.setEnabled(False)
        self.btn_ok.setStyleSheet("color: green; font-weight: bold;")
        self.btn_ok.clicked.connect(self._marcar_ok_clicked)

        self.btn_no_ok = QPushButton("✘  Marcar NO OK")
        self.btn_no_ok.setEnabled(False)
        self.btn_no_ok.setStyleSheet("color: red; font-weight: bold;")
        self.btn_no_ok.clicked.connect(self._marcar_no_ok_clicked)

        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.clicked.connect(self._refrescar)

        # ── Leyenda de colores ──
        leyenda = QHBoxLayout()
        for texto, estado_key in [
            ("● Pendiente", "PENDIENTE"),
            ("● OK", "OK"),
            ("● NO OK / Mecánica", "NO_OK"),
        ]:
            lbl = QLabel(texto)
            color_hex = self._COLORES_ESTADO[estado_key].name()
            lbl.setStyleSheet(f"color: {color_hex}; font-weight: bold;")
            leyenda.addWidget(lbl)
        leyenda.addStretch(1)

        # ── Layout ──
        acciones = QHBoxLayout()
        acciones.addWidget(self.btn_ok)
        acciones.addWidget(self.btn_no_ok)
        acciones.addStretch(1)
        acciones.addWidget(self.btn_refrescar)

        root = QVBoxLayout()
        root.addWidget(QLabel("Motos declaradas por Producción:"))
        root.addLayout(leyenda)
        root.addWidget(self.tree)
        root.addLayout(acciones)

        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

        self._refrescar()

    # ── helpers ──

    def _llenar_tree(self, motos):
        self.tree_model.removeRows(0, self.tree_model.rowCount())
        for m in motos:
            estado = getattr(m, "estado_inspeccion", "PENDIENTE") or "PENDIENTE"
            motivo = getattr(m, "motivo_no_ok", "") or ""
            fecha_hora = m.fecha_hora.strftime("%Y-%m-%d %H:%M:%S") if m.fecha_hora else ""

            fila = [
                QStandardItem(m.numero_chasis),
                QStandardItem(m.numero_motor),
                QStandardItem(str(m.modelo)),
                QStandardItem(str(m.color)),
                QStandardItem(fecha_hora),
                QStandardItem(estado),
                QStandardItem(motivo),
            ]

            color = self._COLORES_ESTADO.get(estado, QColor(0, 0, 0))
            for item in fila:
                item.setForeground(color)

            self.tree_model.appendRow(fila)

        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def _chasis_seleccionado(self) -> str | None:
        indices = self.tree.selectedIndexes()
        if not indices:
            return None
        return self.tree_model.item(indices[0].row(), 0).text()

    def _seleccion_cambiada(self, *_):
        tiene = bool(self._chasis_seleccionado())
        self.btn_ok.setEnabled(tiene)
        self.btn_no_ok.setEnabled(tiene)

    def _refrescar(self):
        motos = self.servicio.listar_todas()
        self._llenar_tree(motos)
        self.btn_ok.setEnabled(False)
        self.btn_no_ok.setEnabled(False)

    # ── acciones ──

    def _marcar_ok_clicked(self):
        chasis = self._chasis_seleccionado()
        if not chasis:
            return

        res = self.servicio.marcar_ok(chasis)
        if res.ok:
            QMessageBox.information(self, "Inspección OK", res.message)
            self.notificar(Evento("inspeccion_marcar_ok", {"chasis": chasis}))
        else:
            QMessageBox.warning(self, "Error", res.message)

        self._refrescar()

    def _marcar_no_ok_clicked(self):
        chasis = self._chasis_seleccionado()
        if not chasis:
            return

        dialogo = DialogoMotivoNoOk(self)
        if dialogo.exec() != QDialog.DialogCode.Accepted:
            return

        motivo = dialogo.motivo_seleccionado()
        res = self.servicio.marcar_no_ok(chasis, motivo)
        if res.ok:
            QMessageBox.information(self, "NO OK - Mecánica", res.message)
            self.notificar(Evento("inspeccion_marcar_no_ok", {"chasis": chasis, "motivo": motivo}))
        else:
            QMessageBox.warning(self, "Error", res.message)

        self._refrescar()
