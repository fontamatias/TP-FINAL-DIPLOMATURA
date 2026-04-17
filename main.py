import sys
import traceback
from PyQt6.QtWidgets import QApplication

from base_de_datos.db import empleados_db
from modelo.empleados import Usuario
from modelo.motos import Moto
from controlador.app_controlador import ControladorDeApp

def main():
    try:
        app = QApplication(sys.argv)

        # inicializa DB/tablas
        empleados_db([Usuario, Moto])

        # arranca flujo UI
        controlador = ControladorDeApp()
        controlador.arranque()

        # loop de eventos Qt
        sys.exit(app.exec())

    except Exception:
        traceback.print_exc()
        input("Enter para cerrar...")

if __name__ == "__main__":
    main()