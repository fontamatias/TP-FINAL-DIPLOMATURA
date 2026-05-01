from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QMessageBox
)

from shared.socket_api import SocketAPI
from shared.config import SERVER_HOST, SERVER_PORT


class VentanaCliente(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cliente - Compra de Motos")

        self.api = SocketAPI(SERVER_HOST, SERVER_PORT)

        self._venta_id: int | None = None
        self._venta_numero: str | None = None

        # ===== UI =====
        self.lbl_pedido = QLabel("Pedido actual: (ninguno)")
        self.lbl_pedido.setStyleSheet("font-weight:bold;")

        self.tree_stock = QTreeWidget()
        self.tree_stock.setColumnCount(5)
        self.tree_stock.setHeaderLabels(["Chasis", "Motor", "Modelo", "Color", "Fecha/Hora"])
        self.tree_stock.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

        self.btn_refrescar = QPushButton("Refrescar stock")
        self.btn_refrescar.clicked.connect(self.refrescar_stock)

        self.btn_crear_pedido = QPushButton("Crear pedido")
        self.btn_crear_pedido.clicked.connect(self.crear_pedido)

        self.btn_agregar = QPushButton("Agregar moto seleccionada al pedido")
        self.btn_agregar.clicked.connect(self.agregar_moto_seleccionada)
        self.btn_agregar.setEnabled(False)

        self.btn_ver_items = QPushButton("Ver items del pedido")
        self.btn_ver_items.clicked.connect(self.ver_items)
        self.btn_ver_items.setEnabled(False)

        self.btn_enviar = QPushButton("Enviar pedido (queda pendiente)")
        self.btn_enviar.clicked.connect(self.enviar_pedido)
        self.btn_enviar.setEnabled(False)

        central = QWidget()
        root = QVBoxLayout(central)

        root.addWidget(self.lbl_pedido)

        root.addWidget(QLabel("Stock disponible (OK_INSPECCION):"))
        root.addWidget(self.tree_stock)

        row = QHBoxLayout()
        row.addWidget(self.btn_refrescar)
        row.addStretch(1)
        row.addWidget(self.btn_crear_pedido)
        row.addWidget(self.btn_agregar)
        row.addWidget(self.btn_ver_items)
        row.addWidget(self.btn_enviar)
        root.addLayout(row)

        self.setCentralWidget(central)

        # carga inicial
        self.refrescar_stock()
        self._actualizar_botones()

    # ===== Helpers =====
    def _actualizar_botones(self):
        tiene_pedido = self._venta_id is not None
        self.btn_agregar.setEnabled(tiene_pedido)
        self.btn_ver_items.setEnabled(tiene_pedido)
        self.btn_enviar.setEnabled(tiene_pedido)

        if not tiene_pedido:
            self.lbl_pedido.setText("Pedido actual: (ninguno)")
        else:
            self.lbl_pedido.setText(f"Pedido actual: {self._venta_numero} (id={self._venta_id})")

    def _moto_seleccionada_chasis(self) -> str | None:
        it = self.tree_stock.currentItem()
        if not it:
            return None
        return it.text(0)

    # ===== API calls =====
    def refrescar_stock(self):
        r = self.api.call("listar_stock_listo")
        if not r.get("ok"):
            QMessageBox.warning(self, "Error", r.get("message") or "No se pudo cargar stock.")
            return

        motos = (r.get("data") or {}).get("motos") or []

        self.tree_stock.clear()
        for m in motos:
            self.tree_stock.addTopLevelItem(QTreeWidgetItem([
                str(m.get("numero_chasis", "")),
                str(m.get("numero_motor", "")),
                str(m.get("modelo", "")),
                str(m.get("color", "")),
                str(m.get("fecha_hora", "")) if m.get("fecha_hora") else "",
            ]))

        for i in range(5):
            self.tree_stock.resizeColumnToContents(i)

    def crear_pedido(self):
        r = self.api.call("crear_pedido")
        if not r.get("ok"):
            QMessageBox.warning(self, "Error", r.get("message") or "No se pudo crear el pedido.")
            return

        venta = (r.get("data") or {}).get("venta") or {}
        self._venta_id = int(venta.get("id"))
        self._venta_numero = str(venta.get("numero_venta"))

        QMessageBox.information(self, "OK", f"Pedido creado. Nro: {self._venta_numero}")
        self._actualizar_botones()

    def agregar_moto_seleccionada(self):
        if self._venta_id is None:
            QMessageBox.warning(self, "Error", "Primero creá un pedido.")
            return

        chasis = self._moto_seleccionada_chasis()
        if not chasis:
            QMessageBox.warning(self, "Error", "Seleccioná una moto del stock.")
            return

        r = self.api.call("agregar_moto_a_pedido", {"venta_id": self._venta_id, "chasis": chasis})
        if not r.get("ok"):
            QMessageBox.warning(self, "Error", r.get("message") or "No se pudo agregar la moto.")
            return

        QMessageBox.information(self, "OK", r.get("message") or "Moto agregada.")
        # al reservar, sale del stock
        self.refrescar_stock()

    def ver_items(self):
        if self._venta_id is None:
            return
        r = self.api.call("items_de_venta", {"venta_id": self._venta_id})
        if not r.get("ok"):
            QMessageBox.warning(self, "Error", r.get("message") or "No se pudieron listar items.")
            return

        items = (r.get("data") or {}).get("items") or []
        texto = "\n".join([f"- {it['numero_chasis']} / {it['numero_motor']}" for it in items]) or "(sin items)"
        QMessageBox.information(self, "Items del pedido", texto)

    def enviar_pedido(self):
        """
        En este modelo no hay acción extra: el pedido ya está PENDIENTE.
        Pero lo dejamos como 'confirmación' para el usuario.
        """
        if self._venta_id is None:
            return

        r = self.api.call("items_de_venta", {"venta_id": self._venta_id})
        items = (r.get("data") or {}).get("items") or []
        if not items:
            QMessageBox.warning(self, "Error", "El pedido no tiene motos. Agregá al menos una.")
            return

        QMessageBox.information(
            self,
            "Pedido enviado",
            f"Pedido {self._venta_numero} enviado.\nAhora Distribución lo verá como PENDIENTE."
        )

        # Resetea pedido actual para comenzar otro
        self._venta_id = None
        self._venta_numero = None
        self._actualizar_botones()