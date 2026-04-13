"""
bienvenida.py
-------------
Vista = venta de bienvenida en patalla.
no conce Login ni db
"""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

class BienvenidoApp(QMainWindow):
    def __init__(self, nombre_usuario:str, sector:str):
        super().__init__()
        self.setWindowTitle("Bienvenido")

        central=QWidget()
        central.setStyleSheet("background-color:white;")
        layout= QVBoxLayout(central)

        label= QLabel(f"Bienvenido, {nombre_usuario}\nSector: {sector}")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font=QFont()
        font.setPointSize(42)
        font.setBold(True)
        label.setFont(font)

        layout.addWidget(label)
        self.setCentralWidget(central)
      
        self.showFullScreen()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
