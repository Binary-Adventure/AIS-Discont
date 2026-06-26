import requests
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from ..config import config

class BaseWindow(QMainWindow):
    API_URL = config.api.url

    def __init__(self, api_key: str, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.user_type = None
        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

    def api_request(self, method: str, endpoint: str, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["X-API-Key"] = self.api_key
        try:
            response = requests.request(
                method=method.upper(), url=f"{self.API_URL}{endpoint}",
                headers=headers, timeout=5, **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Ошибка сети",
                f"Не удалось подключиться к серверу.\nURL: {self.API_URL}\n"
                f"Убедитесь, что сервер запущен: python run_api.py")
            return None
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return None
            QMessageBox.critical(self, "Ошибка API", f"Ошибка {response.status_code}: {response.text}")
            return None
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            return None

    def show_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def show_warning(self, title: str, message: str):
        QMessageBox.warning(self, title, message)

    def confirm_action(self, title: str, message: str) -> bool:
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes