from __future__ import annotations

from datetime import date
from typing import Callable

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QDialog
)

from patrones.observadores import Sujeto, Evento
from app.constantes import Eventos


class DialogoHistorialVentas(QDialog):
    def __init__(self, listar_ventas_finalizadas, items_de_venta, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de ventas (FINALIZADAS)")
        self._listar_ventas_finalizadas = listar_ventas_finalizadas
        self._items_de_venta = items_de_venta

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Nro venta", "Fecha/Hora", "Estado", "Cantidad motos"])

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        layout.addWidget(btn_cerrar)

        self._cargar()

    def _cargar(self):
        self.tree.clear()
        ventas = self._listar_ventas_finalizadas() if self._listar_ventas_finalizadas else []

        for v in ventas:
            items = self._items_de_venta(v.id) if self._items_de_venta else []
            it = QTreeWidgetItem([
                str(v.numero_venta),
                v.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
                str(v.estado),
                str(len(items)),
            ])
            self.tree.addTopLevelItem(it)

        for i in range(4):
            self.tree.resizeColumnToContents(i)


class VentanaDistribucion(QMainWindow, Sujeto):
    def __init__(self, nombre_usuario: str):
        QMainWindow.__init__(self)
        Sujeto.__init__(self)

        self.setWindowTitle(f"Distribución - Usuario: {nombre_usuario}")

        # 4b) callbacks inyectados
        self._listar_stock_listo: Callable[[], list] | None = None
        self._listar_ventas_pendientes: Callable[[], list] | None = None
        self._listar_ventas_finalizadas: Callable[[], list] | None = None
        self._items_de_venta: Callable[[int], list] | None = None
        self._ventas_finalizadas_del_dia: Callable[[date], int] | None = None
        self._motos_vendidas_del_dia: Callable[[date], int] | None = None

        self._dia_actual = date.today()

        self.tree_stock = QTreeWidget()
        self.tree_stock.setColumnCount(5)
        self.tree_stock.setHeaderLabels(["Chasis", "Motor", "Modelo", "Color", "Fecha/Hora"])
        self.tree_stock.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.clicked.connect(self._refrescar)

        self.btn_historial = QPushButton("Historial")
        self.btn_historial.clicked.connect(self._historial_clicked)

        self.btn_cerrar_dia = QPushButton("Cerrar día")
        self.btn_cerrar_dia.clicked.connect(self._cerrar_dia_clicked)

        self.lbl_pedido_actual = QLabel("Pedido actual: (ninguno)")
        self.lbl_pedido_actual.setStyleSheet("font-weight:bold;")

        self.btn_crear_pedido = QPushButton("Crear pedido")
        self.btn_crear_pedido.clicked.connect(self._crear_pedido_clicked)

        self.btn_agregar_a_pedido = QPushButton("Agregar moto seleccionada al pedido")
        self.btn_agregar_a_pedido.clicked.connect(self._agregar_a_pedido_clicked)
        self.btn_agregar_a_pedido.setEnabled(False)

        self.tree_items_pedido = QTreeWidget()
        self.tree_items_pedido.setColumnCount(2)
        self.tree_items_pedido.setHeaderLabels(["Chasis", "Motor"])

        self.tree_pedidos = QTreeWidget()
        self.tree_pedidos.setColumnCount(2)
        self.tree_pedidos.setHeaderLabels(["ID", "Nro venta (pendiente)"])
        self.tree_pedidos.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree_pedidos.itemSelectionChanged.connect(self._pedido_seleccionado)

        self.tree_pedido_detalle = QTreeWidget()
        self.tree_pedido_detalle.setColumnCount(2)
        self.tree_pedido_detalle.setHeaderLabels(["Chasis", "Motor"])

        self.btn_finalizar_pedido = QPushButton("Finalizar pedido seleccionado")
        self.btn_finalizar_pedido.clicked.connect(self._finalizar_pedido_clicked)

        self._venta_actual_id: int | None = None
        self._venta_actual_numero: str | None = None

        central = QWidget()
        root = QVBoxLayout(central)

        root.addWidget(QLabel("Stock listo para venta (OK_INSPECCION):"))
        root.addWidget(self.tree_stock)

        acciones_stock = QHBoxLayout()
        acciones_stock.addWidget(self.btn_refrescar)
        acciones_stock.addWidget(self.btn_historial)
        acciones_stock.addWidget(self.btn_cerrar_dia)
        acciones_stock.addStretch(1)
        root.addLayout(acciones_stock)

        acciones_pedido = QHBoxLayout()
        acciones_pedido.addWidget(self.lbl_pedido_actual)
        acciones_pedido.addStretch(1)
        acciones_pedido.addWidget(self.btn_crear_pedido)
        acciones_pedido.addWidget(self.btn_agregar_a_pedido)
        root.addLayout(acciones_pedido)

        root.addWidget(QLabel("Motos dentro del pedido actual:"))
        root.addWidget(self.tree_items_pedido)

        root.addWidget(QLabel("Pedidos pendientes para salir:"))
        root.addWidget(self.tree_pedidos)

        root.addWidget(QLabel("Detalle del pedido seleccionado:"))
        root.addWidget(self.tree_pedido_detalle)

        acciones_fin = QHBoxLayout()
        acciones_fin.addStretch(1)
        acciones_fin.addWidget(self.btn_finalizar_pedido)
        root.addLayout(acciones_fin)

        self.setCentralWidget(central)

    def set_servicio(
        self,
        *,
        listar_stock_listo,
        listar_ventas_pendientes,
        listar_ventas_finalizadas,
        items_de_venta,
        ventas_finalizadas_del_dia,
        motos_vendidas_del_dia,
    ) -> None:
        self._listar_stock_listo = listar_stock_listo
        self._listar_ventas_pendientes = listar_ventas_pendientes
        self._listar_ventas_finalizadas = listar_ventas_finalizadas
        self._items_de_venta = items_de_venta
        self._ventas_finalizadas_del_dia = ventas_finalizadas_del_dia
        self._motos_vendidas_del_dia = motos_vendidas_del_dia
        self._refrescar()

    def _moto_stock_seleccionada_chasis(self) -> str | None:
        item = self.tree_stock.currentItem()
        if not item:
            return None
        return item.text(0)

    def _pedido_seleccionado_id(self) -> int | None:
        item = self.tree_pedidos.currentItem()
        if not item:
            return None
        try:
            return int(item.text(0))
        except ValueError:
            return None

    def _refrescar_stock(self):
        self.tree_stock.clear()
        motos = self._listar_stock_listo() if self._listar_stock_listo else []
        for m in motos:
            it = QTreeWidgetItem([
                m.numero_chasis,
                m.numero_motor,
                str(m.modelo),
                str(m.color),
                m.fecha_hora.strftime("%Y-%m-%d %H:%M:%S"),
            ])
            self.tree_stock.addTopLevelItem(it)

        for i in range(5):
            self.tree_stock.resizeColumnToContents(i)

    def _refrescar_pedidos(self):
        self.tree_pedidos.clear()
        ventas = self._listar_ventas_pendientes() if self._listar_ventas_pendientes else []
        for v in ventas:
            it = QTreeWidgetItem([str(v.id), str(v.numero_venta)])
            self.tree_pedidos.addTopLevelItem(it)
        self.tree_pedidos.resizeColumnToContents(0)
        self.tree_pedidos.resizeColumnToContents(1)

    def _refrescar_items_pedido_actual(self):
        self.tree_items_pedido.clear()
        if self._venta_actual_id is None:
            return
        items = self._items_de_venta(self._venta_actual_id) if self._items_de_venta else []
        for it in items:
            self.tree_items_pedido.addTopLevelItem(QTreeWidgetItem([it.numero_chasis, it.numero_motor]))
        self.tree_items_pedido.resizeColumnToContents(0)
        self.tree_items_pedido.resizeColumnToContents(1)

    def _refrescar(self):
        self._refrescar_stock()
        self._refrescar_pedidos()
        self._refrescar_items_pedido_actual()
        self._actualizar_estado_botones()

    def _actualizar_estado_botones(self):
        self.btn_agregar_a_pedido.setEnabled(self._venta_actual_id is not None)

        if self._venta_actual_id is None or self._venta_actual_numero is None:
            self.lbl_pedido_actual.setText("Pedido actual: (ninguno)")
        else:
            self.lbl_pedido_actual.setText(f"Pedido actual: {self._venta_actual_numero} (id={self._venta_actual_id})")

    def _crear_pedido_clicked(self):
        self.notificar(Evento(nombre=Eventos.DISTRIBUCION_CREAR_PEDIDO, data={}))

    def _agregar_a_pedido_clicked(self):
        if self._venta_actual_id is None:
            QMessageBox.warning(self, "Error", "Primero creá un pedido.")
            return
        chasis = self._moto_stock_seleccionada_chasis()
        if not chasis:
            QMessageBox.warning(self, "Error", "Seleccioná una moto del stock.")
            return

        self.notificar(Evento(
            nombre=Eventos.DISTRIBUCION_AGREGAR_A_PEDIDO,
            data={"venta_id": self._venta_actual_id, "chasis": chasis}
        ))

    def _pedido_seleccionado(self):
        venta_id = self._pedido_seleccionado_id()
        self.tree_pedido_detalle.clear()
        if venta_id is None:
            return
        items = self._items_de_venta(venta_id) if self._items_de_venta else []
        for it in items:
            self.tree_pedido_detalle.addTopLevelItem(QTreeWidgetItem([it.numero_chasis, it.numero_motor]))
        self.tree_pedido_detalle.resizeColumnToContents(0)
        self.tree_pedido_detalle.resizeColumnToContents(1)

    def _finalizar_pedido_clicked(self):
        venta_id = self._pedido_seleccionado_id()
        if venta_id is None:
            QMessageBox.warning(self, "Error", "Seleccioná un pedido pendiente.")
            return

        self.notificar(Evento(
            nombre=Eventos.DISTRIBUCION_FINALIZAR_PEDIDO,
            data={"venta_id": venta_id}
        ))

    def _historial_clicked(self):
        dlg = DialogoHistorialVentas(
            self._listar_ventas_finalizadas,
            self._items_de_venta,
            parent=self
        )
        dlg.exec()

    def _cerrar_dia_clicked(self):
        ventas = self._ventas_finalizadas_del_dia(self._dia_actual) if self._ventas_finalizadas_del_dia else 0
        motos = self._motos_vendidas_del_dia(self._dia_actual) if self._motos_vendidas_del_dia else 0

        QMessageBox.information(
            self,
            "Cierre de día (Distribución)",
            f"Ventas finalizadas hoy ({self._dia_actual.isoformat()}): {ventas}\n"
            f"Motos despachadas hoy: {motos}\n\n"
            "La ventana se cerrará."
        )

        self.notificar(Evento(
            nombre=Eventos.DISTRIBUCION_CIERRE_DIA,
            data={"dia": self._dia_actual.isoformat(), "ventas": ventas, "motos": motos}
        ))

        self.close()

    def set_pedido_actual(self, venta_id: int | None, numero_venta: str | None):
        self._venta_actual_id = venta_id
        self._venta_actual_numero = numero_venta
        self._actualizar_estado_botones()
        self._refrescar_items_pedido_actual()

    def refrescar(self):
        self._refrescar()