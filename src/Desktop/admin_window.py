from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLineEdit, QPushButton, QTableWidget, QHeaderView,
    QTableWidgetItem, QLabel, QGroupBox, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
from Desktop.base_window import BaseWindow
from Api.api_db import ApiDatabaseManager
from DataBase import DataBaseManager
from config import config

class AdminWindow(BaseWindow):
    """Окно администратора."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.setWindowTitle("Система дисконтных карт - Администратор")
        self.setGeometry(100, 100, 1400, 800)
        
        self.db_manager = DataBaseManager(config)
        self.api_db = ApiDatabaseManager(self.db_manager, "admin", key_id=None)
        
        self.setup_ui()

    def setup_ui(self):
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        self._create_clients_tab()
        self._create_cards_tab()
        self._create_card_types_tab()
        self._create_sources_tab()

    def _enable_table_sorting(self, table: QTableWidget):
        """Включает сортировку по клику на заголовок столбца."""
        header = table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        header.sortIndicatorChanged.connect(lambda col, order: table.sortByColumn(col, order))


    def _create_clients_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        search_group = QGroupBox("Поиск")
        search_layout = QHBoxLayout(search_group)
        
        self.clients_search_input = QLineEdit()
        self.clients_search_input.setPlaceholderText("Поиск по ФИО, телефону...")
        search_layout.addWidget(self.clients_search_input)
        
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self._search_clients)
        search_layout.addWidget(search_btn)
        
        self.clients_search_input.returnPressed.connect(self._search_clients)
        layout.addWidget(search_group)
        
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(5)
        self.clients_table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "Email", "Дата регистрации"])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.clients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._enable_table_sorting(self.clients_table)
        layout.addWidget(self.clients_table)
        
        actions_layout = QHBoxLayout()
        
        self.add_client_btn = QPushButton("Добавить клиента")
        self.add_client_btn.clicked.connect(self._add_client)
        actions_layout.addWidget(self.add_client_btn)
        
        self.delete_client_btn = QPushButton("Удалить")
        self.delete_client_btn.clicked.connect(self._delete_client)
        actions_layout.addWidget(self.delete_client_btn)
        
        self.view_client_btn = QPushButton("Просмотреть карты")
        self.view_client_btn.clicked.connect(self._view_client_cards)
        actions_layout.addWidget(self.view_client_btn)
        
        layout.addLayout(actions_layout)
        
        self._load_clients()
        self.tab_widget.addTab(tab, "Клиенты")

    def _change_card_status(self, is_active: bool):
        row = self.cards_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите карту")
            return
        
        action = "Разблокировать" if is_active else "Заблокировать"
        if QMessageBox.question(self, "Подтверждение", f"{action} выбранную карту?") == QMessageBox.StandardButton.Yes:
            card_id = int(self.cards_table.item(row, 0).text())
            try:
                if is_active:
                    self.api_db.activate_card(card_id)
                else:
                    self.api_db.deactivate_card(card_id)
                self._load_cards()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось {action.lower()} карту:\n{e}")

    def _deactivate_card(self):
        self._change_card_status(False)

    def _activate_card(self):
        self._change_card_status(True)

    def _delete_card(self):
        row = self.cards_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите карту")
            return
        
        if QMessageBox.question(self, "Подтверждение", "Удалить выбранную карту? Это действие нельзя отменить.") == QMessageBox.StandardButton.Yes:
            card_id = int(self.cards_table.item(row, 0).text())
            try:
                self.api_db.delete_card(card_id)
                self._load_cards()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить карту:\n{e}")

    def _create_cards_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.cards_table = QTableWidget()
        self.cards_table.setColumnCount(7)
        self.cards_table.setHorizontalHeaderLabels(["ID", "Номер", "Клиент", "Тип", "Статус", "Дата выдачи", "Баланс"])
        self.cards_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cards_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._enable_table_sorting(self.cards_table)
        layout.addWidget(self.cards_table)
        
        actions_layout = QHBoxLayout()
        
        self.issue_card_btn = QPushButton("Выдать карту")
        self.issue_card_btn.clicked.connect(self._issue_card)
        actions_layout.addWidget(self.issue_card_btn)
        
        self.deactivate_card_btn = QPushButton("Заблокировать")
        self.deactivate_card_btn.clicked.connect(self._deactivate_card)
        actions_layout.addWidget(self.deactivate_card_btn)

        self.activate_card_btn = QPushButton("Разблокировать")
        self.activate_card_btn.clicked.connect(self._activate_card)
        actions_layout.addWidget(self.activate_card_btn)

        self.delete_card_btn = QPushButton("Удалить карту")
        self.delete_card_btn.clicked.connect(self._delete_card)
        actions_layout.addWidget(self.delete_card_btn)
        
        layout.addLayout(actions_layout)
        self._load_cards()
        self.tab_widget.addTab(tab, "Карты")

    def _create_card_types_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.card_types_table = QTableWidget()
        self.card_types_table.setColumnCount(5)
        self.card_types_table.setHorizontalHeaderLabels(["ID", "Название", "Скидка", "Бонусы", "Порог апгрейда"])
        self.card_types_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._enable_table_sorting(self.card_types_table)
        layout.addWidget(self.card_types_table)
        
        actions_layout = QHBoxLayout()
        self.add_type_btn = QPushButton("Добавить тип")
        self.add_type_btn.clicked.connect(self._add_card_type)
        actions_layout.addWidget(self.add_type_btn)
        
        self.delete_type_btn = QPushButton("Удалить")
        self.delete_type_btn.clicked.connect(self._delete_card_type)
        actions_layout.addWidget(self.delete_type_btn)
        layout.addLayout(actions_layout)
        
        self._load_card_types()
        self.tab_widget.addTab(tab, "Типы карт")

    def _create_sources_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.sources_table = QTableWidget()
        self.sources_table.setColumnCount(5)
        self.sources_table.setHorizontalHeaderLabels(["ID", "Тип", "Описание", "Статус", "Дата создания"])
        self.sources_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.sources_table)
        
        actions_layout = QHBoxLayout()
        
        self.add_source_btn = QPushButton("Добавить источник")
        self.add_source_btn.clicked.connect(self._add_source)
        actions_layout.addWidget(self.add_source_btn)
        
        self.delete_source_btn = QPushButton("Удалить")
        self.delete_source_btn.clicked.connect(self._delete_source)
        actions_layout.addWidget(self.delete_source_btn)
        
        self.deactivate_source_btn = QPushButton("Отключить")
        self.deactivate_source_btn.clicked.connect(self._deactivate_source)
        actions_layout.addWidget(self.deactivate_source_btn)
        
        layout.addLayout(actions_layout)
        
        self._load_sources()
        self.tab_widget.addTab(tab, "Источники доступа")

    def _load_clients(self):
        clients = self.api_db.get_all_clients()
        self.clients_table.setRowCount(len(clients))
        for row, client in enumerate(clients):
            self.clients_table.setItem(row, 0, QTableWidgetItem(str(client.client_id)))
            fio = f"{client.last_name} {client.first_name} {client.middle_name or ''}".strip()
            self.clients_table.setItem(row, 1, QTableWidgetItem(fio))
            self.clients_table.setItem(row, 2, QTableWidgetItem(client.phone))
            self.clients_table.setItem(row, 3, QTableWidgetItem(client.email or " "))
            self.clients_table.setItem(row, 4, QTableWidgetItem(str(client.registration_date)))

    def _load_cards(self):
        cards = []
        clients = self.api_db.get_all_clients()
        for client in clients:
            cards.extend(self.api_db.get_cards_by_client(client.client_id))
        
        self.cards_table.setRowCount(len(cards))
        for row, card in enumerate(cards):
            self.cards_table.setItem(row, 0, QTableWidgetItem(str(card.card_id)))
            self.cards_table.setItem(row, 1, QTableWidgetItem(card.card_number))
            self.cards_table.setItem(row, 2, QTableWidgetItem(str(card.client_id)))
            card_type = card.card_type or self.api_db.get_card_type_by_id(card.card_type_id)
            self.cards_table.setItem(row, 3, QTableWidgetItem(card_type.type_name if card_type else " "))
            status = "Активна" if card.is_active else "Заблокирована"
            self.cards_table.setItem(row, 4, QTableWidgetItem(status))
            self.cards_table.setItem(row, 5, QTableWidgetItem(str(card.issue_date)))
            
            try:
                bonus_account = self.api_db.get_bonus_account_by_client(card.client_id)
                if bonus_account:
                    balance = float(bonus_account.balance)
                    balance_item = QTableWidgetItem(f"{balance:.2f}")
                    if balance > 0:
                        balance_item.setForeground(Qt.GlobalColor.darkGreen)
                    self.cards_table.setItem(row, 6, balance_item)
                else:
                    self.cards_table.setItem(row, 6, QTableWidgetItem("0.00"))
            except Exception as e:
                self.cards_table.setItem(row, 6, QTableWidgetItem("—"))

    def _load_card_types(self):
        card_types = self.api_db.get_all_card_types()
        self.card_types_table.setRowCount(len(card_types))
        for row, ct in enumerate(card_types):
            self.card_types_table.setItem(row, 0, QTableWidgetItem(str(ct.card_type_id))) # ID
            self.card_types_table.setItem(row, 1, QTableWidgetItem(ct.type_name))
            self.card_types_table.setItem(row, 2, QTableWidgetItem(f"{ct.discount_percent}%"))
            self.card_types_table.setItem(row, 3, QTableWidgetItem(f"{ct.bonus_accrual_rate}%"))
            self.card_types_table.setItem(row, 4, QTableWidgetItem(str(ct.upgrade_threshold)))

    def _load_sources(self):
        with self.db_manager._get_cursor() as cur:
            cur.execute("""
                SELECT ak.key_id, ak.user_type, ak.description, ak.is_active, ak.created_at
                FROM api_keys ak
                ORDER BY ak.key_id;
            """)
            sources = cur.fetchall()
        
        self.sources_table.setRowCount(len(sources))
        for row, src in enumerate(sources):
            self.sources_table.setItem(row, 0, QTableWidgetItem(str(src[0])))
            self.sources_table.setItem(row, 1, QTableWidgetItem(src[1]))
            self.sources_table.setItem(row, 2, QTableWidgetItem(src[2] or " "))
            status = "Активен" if src[3] else "Отключен"
            self.sources_table.setItem(row, 3, QTableWidgetItem(status))
            self.sources_table.setItem(row, 4, QTableWidgetItem(str(src[4])[:19] if src[4] else " "))

    def _search_clients(self):
        text = self.clients_search_input.text().strip()
        if not text:
            self._load_clients()
            return
        
        try:
            response = self.api_request("GET", f"/clients/search?query={text}")
            clients = response or []
            self.clients_table.setRowCount(len(clients))
            for row, client in enumerate(clients):
                self.clients_table.setItem(row, 0, QTableWidgetItem(str(client.get("client_id", ""))))
                fio = f"{client.get('last_name', '')} {client.get('first_name', '')} {client.get('middle_name', '') or ''}".strip()
                self.clients_table.setItem(row, 1, QTableWidgetItem(fio))
                self.clients_table.setItem(row, 2, QTableWidgetItem(client.get("phone", "")))
                self.clients_table.setItem(row, 3, QTableWidgetItem(client.get("email", "")))
                self.clients_table.setItem(row, 4, QTableWidgetItem(client.get("registration_date", "")))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска: {e}")

    def _add_client(self):
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.api_db.create_client(**data)
            self._load_clients()

    def _delete_client(self):
        row = self.clients_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента")
            return
        
        if QMessageBox.question(self, "Подтверждение", "Удалить выбранного клиента?") == QMessageBox.StandardButton.Yes:
            client_id = int(self.clients_table.item(row, 0).text())
            self.api_db.delete_client(client_id)
            self._load_clients()

    def _view_client_cards(self):
        row = self.clients_table.currentRow()
        if row < 0:
            return
        
        client_id = int(self.clients_table.item(row, 0).text())
        cards = self.api_db.get_cards_by_client(client_id)
        
        if not cards:
            QMessageBox.information(self, "Инфо", "У клиента нет карт")
            return
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Карты клиента")
        msg.setText(f"Карт клиента: {len(cards)}")
        msg.exec()

    def _issue_card(self):
        dialog = IssueCardDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data and data['client_id']:  # Проверяем что клиент выбран
                self.api_db.create_card(data['client_id'], data['card_number'], data.get('card_type_id'))
                self._load_cards()

    def _deactivate_card(self):
        row = self.cards_table.currentRow()
        if row < 0:
            return
        
        if QMessageBox.question(self, "Подтверждение", "Заблокировать выбранную карту?") == QMessageBox.StandardButton.Yes:
            card_id = int(self.cards_table.item(row, 0).text())
            self.api_db.deactivate_card(card_id)
            self._load_cards()

    def _add_card_type(self):
        dialog = CardTypeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:  # Проверяем что данные валидны
                self.api_db.create_card_type(**data)
                self._load_card_types()

    def _delete_card_type(self):
        row = self.card_types_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите тип карты")
            return
        
        card_type_id = int(self.card_types_table.item(row, 0).text())
        if QMessageBox.question(self, "Подтверждение", "Удалить выбранный тип карты?") == QMessageBox.StandardButton.Yes:
            try:
                self.api_db.delete_card_type(card_type_id)
                self._load_card_types()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить тип карты:\n{e}")

    def _add_source(self):
        dialog = SourceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                api_key = self.api_db.create_source(
                    user_type=data['user_type'],
                    user_id=data.get('store_id'),
                    description=data['description']
                )
                self._show_api_key(api_key)
                self._load_sources()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать источник доступа:\n{e}")

    def _show_api_key(self, api_key: str):
        dialog = QDialog(self)
        dialog.setWindowTitle("Сгенерированный API ключ")
        dialog.resize(500, 200)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("API ключ сгенерирован. Скопируйте его, он отображается только один раз!")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        key_input = QLineEdit(api_key)
        key_input.setReadOnly(True)
        key_input.selectAll()
        layout.addWidget(key_input)
        
        btn = QPushButton("Закрыть")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn)
        
        dialog.exec()

    def _delete_source(self):
        row = self.sources_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите источник")
            return
        
        if QMessageBox.question(self, "Подтверждение", "Удалить выбранный источник доступа?") == QMessageBox.StandardButton.Yes:
            key_id = int(self.sources_table.item(row, 0).text())
            try:
                with self.db_manager._get_cursor() as cur:
                    cur.execute("DELETE FROM api_keys WHERE key_id = %s;", (key_id,))
                self.db_manager.conn.commit()
                self._load_sources()
            except Exception as e:
                self.db_manager.conn.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить источник:\n{e}")

    def _deactivate_source(self):
        row = self.sources_table.currentRow()
        if row < 0:
            return
        
        if QMessageBox.question(self, "Подтверждение", "Отключить выбранный источник доступа?") == QMessageBox.StandardButton.Yes:
            key_id = int(self.sources_table.item(row, 0).text())
            try:
                with self.db_manager._get_cursor() as cur:
                    cur.execute("UPDATE api_keys SET is_active = FALSE WHERE key_id = %s;", (key_id,))
                self.db_manager.conn.commit()
                self._load_sources()
            except Exception as e:
                self.db_manager.conn.rollback()
                self._load_sources()


class ClientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление клиента")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.middle_name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        form.addRow("Имя *:", self.first_name_input)
        form.addRow("Фамилия *:", self.last_name_input)
        form.addRow("Отчество:", self.middle_name_input)
        form.addRow("Телефон *:", self.phone_input)
        form.addRow("Email:", self.email_input)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_ok(self):
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        phone = self.phone_input.text().strip()
        
        if not first_name or not last_name or not phone:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        
        import re
        if not re.match(r'^\+?[\d\s\-()]{10,}$', phone):
            QMessageBox.warning(self, "Ошибка", "Неверный формат телефона")
            return
        
        self.accept()

    def get_data(self):
        return {
            "first_name": self.first_name_input.text().strip(),
            "last_name": self.last_name_input.text().strip(),
            "middle_name": self.middle_name_input.text().strip() or None,
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip() or None
        }


class IssueCardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выдача карты")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Поле для поиска клиента
        search_layout = QHBoxLayout()
        self.client_search_input = QLineEdit()
        self.client_search_input.setPlaceholderText("Поиск клиента по телефону...")
        self.client_search_button = QPushButton("Найти")
        search_layout.addWidget(self.client_search_input)
        search_layout.addWidget(self.client_search_button)
        
        form.addRow("Клиент:", search_layout)
        
        self.selected_client_label = QLabel("Выбран: -")
        self.selected_client_label.setStyleSheet("color: green; font-weight: bold;")
        form.addRow("Выбран клиент:", self.selected_client_label)
        
        self.client_id_input = QLineEdit()
        self.client_id_input.setVisible(False)
        
        self.card_number_input = QLineEdit()
        
        form.addRow("ID клиента:", self.client_id_input)
        form.addRow("Номер карты:", self.card_number_input)
        
        # Загрузить типы карт
        try:
            response = self.parent().api_request("GET", "/card_types")
            card_types = response or []
            self.card_type_combo = QComboBox()
            for ct in card_types:
                self.card_type_combo.addItem(f"{ct.get('type_name', '')} ({ct.get('discount_percent', 0)}%)", ct.get('card_type_id'))
        except:
            self.card_type_combo = QComboBox()
            self.card_type_combo.addItem("Нет типов", None)
        
        form.addRow("Тип карты:", self.card_type_combo)
        
        layout.addLayout(form)
        
        # Кнопка найти клиента
        self.client_search_button.clicked.connect(self._search_client_for_issue)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _search_client_for_issue(self):
        """Поиск клиента для выдачи карты (по телефону или ФИО)."""
        search_text = self.client_search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "Ошибка", "Введите телефон или ФИО клиента")
            return
        
        try:
            # Используем универсальный поиск как в основном окне
            response = self.parent().api_request("GET", f"/clients/search?query={search_text}")
            clients = response or []
            
            if clients:
                # Берем первого найденного клиента
                client = clients[0]
                self.selected_client_label.setText(f"Выбран: {client.get('last_name', '')} {client.get('first_name', '')}")
                self.selected_client_label.setStyleSheet("color: green; font-weight: bold;")
                self.client_id_input.setText(str(client.get('client_id', '')))
            else:
                QMessageBox.information(self, "Инфо", "Клиент не найден. Создайте его в разделе 'Клиенты'")
                self.selected_client_label.setText("Выбран: -")
                self.selected_client_label.setStyleSheet("color: red; font-weight: bold;")
                self.client_id_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка поиска клиента: {e}")
            self.selected_client_label.setText("Выбран: -")
            self.selected_client_label.setStyleSheet("color: red; font-weight: bold;")

    def _on_ok(self):
        """Проверка перед созданием карты."""
        # Проверить что клиент выбран
        if not self.client_id_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Сначала найдите и выберите клиента!")
            return
        
        # Проверить что номер карты введен
        if not self.card_number_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите номер карты!")
            return
        
        self.accept()

    def get_data(self):
        client_id_text = self.client_id_input.text().strip()
        
        if not client_id_text:
            QMessageBox.warning(self, "Ошибка", "Сначала найдите и выберите клиента!")
            return None
        
        return {
            "client_id": int(client_id_text),
            "card_number": self.card_number_input.text().strip(),
            "card_type_id": self.card_type_combo.currentData()
        }

class CardTypeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление типа карты")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.type_name_input = QLineEdit()
        self.discount_input = QLineEdit("0.00")
        self.bonus_input = QLineEdit("0.00")
        self.threshold_input = QLineEdit("0.00")
        
        form.addRow("Название:", self.type_name_input)
        form.addRow("Скидка (%):", self.discount_input)
        form.addRow("Бонусы (%):", self.bonus_input)
        form.addRow("Порог апгрейда:", self.threshold_input)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        try:
            discount = float(self.discount_input.text())
            bonus = float(self.bonus_input.text())
            threshold = float(self.threshold_input.text())
            
            # Проверка на максимальное значение
            if discount > 999.99 or bonus > 999.99 or threshold > 999.99:
                QMessageBox.warning(
                    self, "Ошибка", 
                    "Значения не могут превышать 999.99\n"
                    "Измените тип данных в таблице или введите меньшие значения"
                )
                return None
            
            return {
                "type_name": self.type_name_input.text().strip(),
                "discount_percent": discount,
                "bonus_accrual_rate": bonus,
                "upgrade_threshold": threshold
            }
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректные числа")
            return None


class SourceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление источника доступа")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItem("Филиал", "user")
        
        self.description_input = QLineEdit()
        
        form.addRow("Тип пользователя:", self.user_type_combo)
        form.addRow("Описание:", self.description_input)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "user_type": self.user_type_combo.currentData(),
            "description": self.description_input.text().strip() or None
        }