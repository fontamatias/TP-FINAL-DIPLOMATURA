"""
registroUi.py
-----------------

no escribe en db
solo recoge inpurs y llama on_regitro del controlador
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout,QFormLayout,QLineEdit,
    QPushButton,QLabel,QComboBox
)
from modelo.sectores import SECTORES_PERMITIDOS

class VistaRegistro(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro")
        self.setModal(True)

        #calback que el controlador inyecta
        self.activar_registro = None #callable(nombre de usuario, contraseña 1 y 2, sector)

        self.nombre_usuario_input = QLineEdit()
        self.nombre_usuario_input.setPlaceholderText("Usuario")

        self.contraseña_input=QLineEdit()
        self.contraseña_input.setPlaceholderText("Contraseña")
        self.contraseña_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.contraseña2_input=QLineEdit()
        self.contraseña2_input.setPlaceholderText("Confirmar Contraseña")
        self.contraseña2_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.sector_combo = QComboBox()
        self.sector_combo.addItems(SECTORES_PERMITIDOS)

        hint= QLabel (
            "crea tu cuenta para luego entrar al programa \n\n"
            "Usuario:\n- 3 a 20 caracteres \n latras numeros y guion bajo\n\n "
            "Contraseña:\n - 8+ caracteres\n- 1 mayuscula\n 1 miniscula \n 1 numero \n 1 simbolo"
        )
        hint.setStyleSheet("color:#444")

        self.crear_button=QPushButton("Crear Usuario")
        self.crear_button.clicked.connect(self._crear_clicked)

        self.cancelar_button=QPushButton("Cancelar")
        self.cancelar_button.clicked.connect(self.reject)

        form=QFormLayout()
        form.addRow("Usuario:", self.nombre_usuario_input)
        form.addRow("Contraseña:", self.contraseña_input)
        form.addRow("Confirmar contraseña:", self.contraseña2_input)
        form.addRow("Sector:", self.sector_combo)

        layout = QVBoxLayout()
        layout.addWidget(hint)
        layout.addLayout(form)
        layout.addWidget(self.crear_button)
        layout.addWidget(self.cancelar_button)
        self.setLayout(layout)

    def tomar_nombre_de_usuario(self) -> str:
        return self.nombre_usuario_input.text().strip()

    def tomar_sector(self) -> str:
        return self.sector_combo.currentText().strip()
    

    def _crear_clicked(self):
        if callable(self.activar_registro):
            self.activar_registro(
                self.nombre_usuario_input.text(),
                self.contraseña_input.text(),
                self.contraseña2_input.text(),
                self.tomar_sector(),
            )
    
