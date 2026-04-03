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
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import(
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton
)

class PresentacionLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setModal(True)

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
        self.link_registro.setFlat(True)
        self.link_registro.setCursor(Qt.CursorShape.PointingHandCursor)
        self.link_registro.clicked.connect(self._registro_clicked)

        self.exit_button = QPushButton("Salir")
        self.exit_button.clicked.connect(self.reject)

        form = QFormLayout()
        form.addRow("Usuario:",self.nombre_usuario_input)
        form.addRow("Contraseña:", self.contraseña_input)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.iniciar_button)
        layout.addWidget(self.link_registro, alignment=Qt.AlignmentFlag.AlignCenter)
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