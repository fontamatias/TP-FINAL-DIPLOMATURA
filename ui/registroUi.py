"""
registroUi.py
-----------------
no escribe en db
solo recoge inputs y emite evento
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import Qt
from patrones.observadores import Sujeto, Evento


class VistaRegistro(QDialog, Sujeto):
    def __init__(self):
        QDialog.__init__(self)
        Sujeto.__init__(self)

        self.setWindowTitle("Registro")
        self.setModal(True)

        self.nombre_usuario_input = QLineEdit()
        self.nombre_usuario_input.setPlaceholderText("Usuario")

        self.contraseña_input = QLineEdit()
        self.contraseña_input.setPlaceholderText("Contraseña")
        self.contraseña_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.contraseña2_input = QLineEdit()
        self.contraseña2_input.setPlaceholderText("Confirmar Contraseña")
        self.contraseña2_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.sector_input = QComboBox()
        self.sector_input.addItems([
            "Linea de produccion",
            "Mecanica",
            "Inspeccion final",
            "Distribucion",
        ])

        ayuda_usuario = QLabel(
            "Requisitos de usuario:\n"
            "- 3 a 20 caracteres\n"
            "- letras, numeros, punto y guion bajo\n"
        )
        ayuda_usuario.setStyleSheet("color:#444; font-size:11px;")
        ayuda_usuario.setWordWrap(True)

        ayuda_contraseña = QLabel(
            "Requisitos de contraseña:\n"
            "- 8+ caracteres\n"
            "- 1 mayuscula, 1 miniscula, 1 numero y 1 simbolo\n"
        )
        ayuda_contraseña.setStyleSheet("color:#444; font-size:11px;")
        ayuda_contraseña.setWordWrap(True)

        self.crear_button = QPushButton("Crear Usuario")
        self.crear_button.clicked.connect(self._crear_clicked)

        self.cancelar_button = QPushButton("Cancelar")
        self.cancelar_button.clicked.connect(self.reject)

        form = QFormLayout()
        form.addRow("Usuario:", self.nombre_usuario_input)
        form.addRow("", ayuda_usuario)
        form.addRow("Contraseña:", self.contraseña_input)
        form.addRow("", ayuda_contraseña)
        form.addRow("Confirmar contraseña:", self.contraseña2_input)
        form.addRow("Sector:", self.sector_input)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.crear_button)
        layout.addWidget(self.cancelar_button)
        self.setLayout(layout)

    def tomar_nombre_de_usuario(self) -> str:
        return self.nombre_usuario_input.text().strip()

    def tomar_sector(self) -> str:
        return self.sector_input.currentText().strip()

    def _crear_clicked(self):
        self.notificar(Evento(
            nombre="registro_submit",
            data={
                "usuario": self.nombre_usuario_input.text(),
                "c1": self.contraseña_input.text(),
                "c2": self.contraseña2_input.text(),
                "sector": self.tomar_sector(),
            }
        ))