import sys
from PyQt6.QtWidgets import QApplication

from cliente_comprador.ui_cliente import VentanaCliente


def main():
    app = QApplication(sys.argv)
    w = VentanaCliente()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()