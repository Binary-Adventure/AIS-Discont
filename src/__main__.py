import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from PyQt6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QLineEdit, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import requests
from config import config

class AuthDialog(QDialog):
    """Диалог авторизации."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.api_key = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Система дисконтных карт")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        layout.addWidget(QLabel("\nAPI ключ:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Введите API ключ")
        self.api_key_input.setMinimumHeight(35)
        layout.addWidget(self.api_key_input)
        
        self.api_key_input.textChanged.connect(self._on_key_change)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.resize(450, 200)

    def _on_key_change(self, text: str):
        self.ok_button.setEnabled(len(text.strip()) > 0)

    def get_api_key(self) -> str:
        return self.api_key_input.text().strip()

def main():
    app = QApplication(sys.argv)

    auth_dialog = AuthDialog()
    if auth_dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    api_key = auth_dialog.get_api_key()

    try:
        response = requests.post(
            f"{config.api.url}/auth",
            json={"api_key": api_key},
            timeout=5
        )
        
        if response.status_code != 200:
            QMessageBox.critical(None, "Ошибка", "Неверный API ключ")
            sys.exit(1)
            
        data = response.json()
        if not data.get("success"):
            QMessageBox.critical(None, "Ошибка", "API ключ неактивен или недействителен")
            sys.exit(1)
            
        mode = data.get("user_type")
        if mode not in ["admin", "user"]:
            QMessageBox.critical(None, "Ошибка", "Неверный тип пользователя")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        QMessageBox.critical(
            None, 
            "Ошибка подключения",
            f"Не удалось подключиться к серверу API.\n"
            f"URL: {config.api.url}\n"
            f"Убедитесь, что сервер запущен:\npython run_api.py"
        )
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Не удалось подключиться к серверу:\n{e}")
        sys.exit(1)

    try:
        if mode == "user":
            from Desktop.user_window import UserWindow
            window = UserWindow(api_key)
        else:
            from Desktop.admin_window import AdminWindow
            window = AdminWindow(api_key)

        window.show()
        sys.exit(app.exec())
    except ImportError as e:
        QMessageBox.critical(
            None, 
            "Ошибка импорта", 
            f"Не удалось загрузить модуль:\n{e}\n\n"
            f"Убедитесь, что папка Desktop существует и содержит необходимые файлы."
        )
        sys.exit(1)

if __name__ == '__main__':
    main()