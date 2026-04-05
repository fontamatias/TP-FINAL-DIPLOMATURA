from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton,QLabel
)
from PyQt6.QtCore import Qt

class VistaCambiarContraseña(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cambiar contraseña")
        self.setModal(True)

        self.activar_cambio=None
        
        self.usuario_input=QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")

        self.actual_input = QLineEdit()
        self.actual_input.setPlaceholderText("Contraseña actual")
        self.actual_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.nueva1_input = QLineEdit()
        self.nueva1_input.setPlaceholderText("Nueva Contraseña")
        self.nueva1_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.nueva2_input = QLineEdit()
        self.nueva2_input.setPlaceholderText("Confirmar nueva contraseña")
        self.nueva2_input.setEchoMode(QLineEdit.EchoMode.Password)

        hint = QLabel(
            "La nueva contraseña debe cumplir:\n"
            "-8+ caracteres\n -1 mayuscula\n -1 miniscula\n-1 numero\n-1simbolo\n"

        )
        hint.setStyleSheet("color:#444")
        
        self.guardar_button=QPushButton("Guardar")
        self.guardar_button.clicked.connect(self._guardar_clicked)

        self.cancelar_button = QPushButton("Cancelar")
        self.cancelar_button.clicked.connect(self.reject)

        form = QFormLayout()
        form.addRow("Usuario:",self.usuario_input)
        form.addRow("Contraseña actual", self.actual_input)
        form.addRow("Contraseña nueva", self.nueva1_input)
        form.addRow("Confirmar contraseña", self.nueva2_input)

        layout=QVBoxLayout()
        layout.addWidget(hint)
        layout.addLayout(form)
        layout.addWidget(self.guardar_button)
        layout.addWidget(self.cancelar_button)
        self.setLayout(layout)

    def _guardar_clicked(self):
        if callable(self.activar_cambio):
            self.activar_cambio(
                self.usuario_input.text(),
                self.actual_input.text(),
                self.nueva1_input.text(),
                self.nueva2_input.text()
            )

    def set_usuario(self, u:str)->None:
        self.usuario_input.setText((u or "").strip())
        self.actual_input.setFocus()