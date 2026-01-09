from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QStackedWidget,
)
from PyQt5.QtCore import QTimer

from auth_manager import login_user, register_user, is_locked  # record_failed_attempt géré dans login_user


class AuthWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("🔐 Accès Système")
        self.setFixedSize(420, 420)

        # --- StackedWidget contenant les 2 pages ---
        self.stack = QStackedWidget()

        self.login_page = self._build_login_page()
        self.register_page = self._build_register_page()

        self.stack.addWidget(self.login_page)     # index 0
        self.stack.addWidget(self.register_page)  # index 1

        self.setCentralWidget(self.stack)

    # ---------- PAGE LOGIN ----------
    def _build_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("CONNEXION")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #000000;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Nom d'utilisateur :"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Mot de passe :"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("SE CONNECTER")
        layout.addWidget(self.login_button)

        switch_btn = QPushButton("Créer un compte")
        switch_btn.setFlat(True)
        switch_btn.setStyleSheet("color: #3498db;")
        layout.addWidget(switch_btn)

        layout.addStretch()

        self.login_button.clicked.connect(self.handle_login)
        switch_btn.clicked.connect(self.show_register_page)

        return page

    # ---------- PAGE REGISTER ----------
    def _build_register_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("CRÉATION DE COMPTE")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #000000;")
        layout.addWidget(title)

        layout.addWidget(QLabel("Nom d'utilisateur :"))
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choisissez un nom d'utilisateur")
        layout.addWidget(self.reg_username)

        layout.addWidget(QLabel("Email :"))
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Votre adresse email")
        layout.addWidget(self.reg_email)

        layout.addWidget(QLabel("Mot de passe :"))
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Choisissez un mot de passe")
        self.reg_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_password)

        layout.addWidget(QLabel("Confirmer le mot de passe :"))
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Retapez le mot de passe")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_confirm)

        self.register_button = QPushButton("Créer un compte")
        layout.addWidget(self.register_button)

        switch_btn = QPushButton("Déjà inscrit ? Se connecter")
        switch_btn.setFlat(True)
        switch_btn.setStyleSheet("color: #3498db;")
        layout.addWidget(switch_btn)

        layout.addStretch()

        self.register_button.clicked.connect(self.handle_register)
        switch_btn.clicked.connect(self.show_login_page)

        return page

    # ---------- NAVIGATION ----------
    def show_login_page(self):
        self.stack.setCurrentIndex(0)

    def show_register_page(self):
        self.stack.setCurrentIndex(1)

    # ---------- LOGIQUE LOGIN ----------
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Remplissez tous les champs.")
            return

        # --- Protection brute force ---
        if is_locked(username):
            QMessageBox.warning(
                self,
                "Compte bloqué",
                "Trop de tentatives échouées. Réessayez dans 1 minute."
            )
            return

        success, role, message = login_user(username, password)

        if success:
            QMessageBox.information(self, "Succès", message)
            self.open_main_window(role, username)
        else:
            QMessageBox.warning(self, "Erreur", message)

    # ---------- LOGIQUE REGISTER ----------
    def handle_register(self):
        username = self.reg_username.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_password.text().strip()
        confirm = self.reg_confirm.text().strip()

        if not username or not email or not password or not confirm:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            return

        success, message = register_user(username, password, "client", email)

        if success:
            QMessageBox.information(self, "Succès", message)
            self.show_login_page()
        else:
            QMessageBox.warning(self, "Erreur", message)

    # ---------- OUVERTURE FENÊTRES PRINCIPALES ----------
    def open_main_window(self, role: str, username: str):
        try:
            if role == "admin":
                from admin_window import AdminMainWindow
                self.admin_window = AdminMainWindow(username)
                self.admin_window.show()
            else:
                from main import ClientMainWindow
                self.client_window = ClientMainWindow(username)
                self.client_window.show()

            QTimer.singleShot(200, self.close)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur ouverture fenêtre: {e}")
