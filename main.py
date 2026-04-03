"""
main.py

"""

import sys
from  PyQt6.QtWidgets import QApplication

from base_de_datos.login import empleados_db
from modelo.empleados import Usuario
from controlador.app_controlador import ControladordDeApp

def main():
    empleados_db([Usuario])

    app = QApplication(sys.argv)

    controlador = ControladordDeApp()
    controlador.arranque()

    #NOTA
    #- EL CONTROLADOR ABRE BIENVENIDOS Y CIERRA DIALOGOLOGIN
    #- AQUI SOLO EJECUTMOS EL LOOP DE EVNTOS.
    sys.exit(app.exec())

if __name__=="__main__":
    main()