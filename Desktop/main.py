from PyQt6.QtWidgets import QApplication, QMessageBox
from ..config import config
from ..Desktop.main_window import AuthDialog


import sys
import requests

def main():
    app = QApplication(sys.argv)
    
    auth_dialog = AuthDialog()
    
    if auth_dialog.exec() != auth_dialog.DialogCode.Accepted:
        sys.exit(0)

    api_key = auth_dialog.get_api_key()

    try:
        response = requests.post(
            f"{config.api.url}/auth",
            json={"api_key": api_key},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            QMessageBox.critical(None, "Ошибка авторизации", data.get("message", "Неверный API ключ"))
            sys.exit(1)
        
        user_type = data.get("user_type")
        
        if user_type == "admin":
            from ..Desktop.admin_window import AdminWindow
            window = AdminWindow(api_key)
        else:
            from ..Desktop.user_window import UserWindow
            window = UserWindow(api_key)
        
        window.show()
        sys.exit(app.exec())
        
    except requests.exceptions.ConnectionError:
        QMessageBox.critical(
            None, "Ошибка подключения", 
            f"Не удалось подключиться к серверу API.\nУбедитесь, что сервер запущен на {config.api.url}"
        )
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Произошла ошибка:\n{e}")
        sys.exit(1)

if __name__ == '__main__':
    main()