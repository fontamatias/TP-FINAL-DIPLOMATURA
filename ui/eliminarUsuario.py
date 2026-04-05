from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel
)

class VistaEliminarUsuario(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eliminar usuario")
        self.setModal(True)

        self.activar_eliminacion = None

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")

        self.actual_input = QLineEdit()
        self.actual_input.setPlaceholderText("Contraseña actual")
        self.actual_input.setEchoMode(QLineEdit.EchoMode.Password)

        advertencia = QLabel(
            "Esta acción eliminará el usuario.\n"
            "No se puede deshacer."
        )
        advertencia.setStyleSheet("color:#a00")

        self.eliminar_button = QPushButton("Eliminar")
        self.eliminar_button.clicked.connect(self._eliminar_clicked)

        self.cancelar_button = QPushButton("Cancelar")
        self.cancelar_button.clicked.connect(self.reject)

        form = QFormLayout()
        form.addRow("Usuario:", self.usuario_input)
        form.addRow("Contraseña actual:", self.actual_input)

        layout = QVBoxLayout()
        layout.addWidget(advertencia)
        layout.addLayout(form)
        layout.addWidget(self.eliminar_button)
        layout.addWidget(self.cancelar_button)
        self.setLayout(layout)

    def _eliminar_clicked(self):
        if callable(self.activar_eliminacion):
            self.activar_eliminacion(
                self.usuario_input.text(),
                self.actual_input.text()
            )

    def set_usuario(self, u: str) -> None:
        self.usuario_input.setText((u or "").strip())
        self.actual_input.setFocus()