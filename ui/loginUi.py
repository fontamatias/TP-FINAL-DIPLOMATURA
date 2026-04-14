"""
loginUi.py
-----------
vista del login

regla:
- la vista no valida contra db
- la vista solo:
    -recoge inputs
    - llama callbacks que el controlador define
"""
from PyQt6.QtGui import QPixmap
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import(
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton,QLabel
)

class PresentacionLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setModal(True)
        self.on_cambiar_contrasena = None
        self.on_eliminar_usuario = None

        #llamadas que el controlador inyecta

        self.on_login = None # llamada (nombre_usuario, contraseña)
        self.on_abrir_registro = None#llamada ()

        self.nombre_usuario_input = QLineEdit()
        self.nombre_usuario_input.setPlaceholderText("Usuario")

        self.contraseña_input = QLineEdit()
        self.contraseña_input.setPlaceholderText("Contraseña")
        self.contraseña_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.iniciar_button = QPushButton("Iniciar sesion")
        self.iniciar_button.clicked.connect(self._login_clicked)

        self.link_registro=QPushButton("Eres nuevo? REGISTRATE!")
        self.link_registro.clicked.connect(self._registro_clicked)
        
        self.cambiar_contraseña_button=QPushButton("Cambiar contraseña")
        self.cambiar_contraseña_button.clicked.connect(self._contrasenia_clicked)

        self.eliminar_usuario_button = QPushButton("Eliminar usuario")
        self.eliminar_usuario_button.clicked.connect(self._eliminar_usuario_clicked)

        self.exit_button = QPushButton("Salir")
        self.exit_button.clicked.connect(self.reject)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        base_dir = os.path.dirname(__file__)
        img_path = os.path.join(base_dir, "producto_33.jpg")
        pix = QPixmap(img_path)

        if pix.isNull():
            print(f"No se pudo cargar imagen: {img_path}")
        else:
            # Escala y reserva espacio para que se vea sí o sí
            pix = pix.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setFixedHeight(pix.height() + 10)   # fuerza lugar en el layout

        form = QFormLayout()
        form.addRow("Usuario:",self.nombre_usuario_input)
        form.addRow("Contraseña:", self.contraseña_input)

        layout = QVBoxLayout()
        layout.addWidget(logo)
        layout.addLayout(form)
        layout.addWidget(self.iniciar_button)
        layout.addWidget(self.link_registro)
        layout.addWidget(self.cambiar_contraseña_button)
        layout.addWidget(self.eliminar_usuario_button)
        layout.addWidget(self.exit_button)
        self.setLayout(layout)


    #metodos helpers para el controlador puede manipular la vist
    def set_nombre_usuario(self,nombre_usuario:str) ->None:
        self.nombre_usuario_input.setText(nombre_usuario or "")

    def contraseña_focus(self) -> None:
        self.contraseña_input.setFocus()


    #eventos internos

    def _login_clicked(self):
        if callable(self.on_login):
            self.on_login(self.nombre_usuario_input.text(), self.contraseña_input.text ())

    def _registro_clicked(self):
        if callable(self.on_abrir_registro):
            self.on_abrir_registro()

    def _contrasenia_clicked(self):
        if callable(self.on_cambiar_contrasena):
            self.on_cambiar_contrasena()

    def _eliminar_usuario_clicked(self):
        if callable(self.on_eliminar_usuario):
            self.on_eliminar_usuario()