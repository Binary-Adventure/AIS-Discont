"""Основное окно приложения."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLineEdit, QPushButton, QTableWidget, QHeaderView,
    QTableWidgetItem, QLabel, QGroupBox, QFrame, QSizePolicy, 
    QMessageBox, QDialog, QLineEdit, QDialogButtonBox, QApplication
)


class AuthDialog(QDialog):
    """Диалог авторизации."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.api_key = None
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Введите API ключ")
        layout.addWidget(QLabel("API ключ:"))
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
        
        self.resize(400, 150)
    
    def _on_key_change(self, text: str):
        self.ok_button.setEnabled(len(text.strip()) > 0)
    
    def get_api_key(self) -> str:
        return self.api_key_input.text().strip()


class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    API_URL = "http://localhost:8000"
    
    def __init__(self, api_key: str):
        super().__init__()
        self.setWindowTitle("Система дисконтных карт")
        self.setGeometry(100, 100, 1400, 800)
        
        self.api_key = api_key
        self.user_type = None
        
        self._init_ui()
        """Инициализация интерфейса."""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Меню инструментов (вкладки)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Создание вкладок
        self._create_users_tab()
        self._create_cards_tab()
        self._create_shops_tab()
        
        # Если не админ, скрываем некоторые вкладки
        if self.user_type != "admin":
            # В будущем можно добавить вкладку для бонусов
            pass
    
    def _create_users_tab(self):
        """Создание вкладки 'Пользователи'."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Левая панель (поиск и фильтры)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Поиск
        search_group = QGroupBox("Поиск")
        search_layout = QVBoxLayout(search_group)
        
        self.users_search_input = QLineEdit()
        self.users_search_input.setPlaceholderText("ID, ФИО или телефон...")
        self.users_search_input.textChanged.connect(self._filter_users)
        
        self.users_search_button = QPushButton("Найти")
        self.users_search_button.clicked.connect(lambda: self._filter_users(self.users_search_input.text()))
        
        search_layout.addWidget(self.users_search_input)
        search_layout.addWidget(self.users_search_button)
        
        left_panel.addWidget(search_group)
        
        # Фильтры
        filters_group = QGroupBox("Фильтры по картам")
        filters_layout = QVBoxLayout(filters_group)
        filters_layout.setSpacing(5)
        
        self.filter_card_type = QPushButton("Тип карты...")
        self.filter_card_type.clicked.connect(lambda: print("Фильтр: тип карты"))
        
        self.filter_card_status = QPushButton("Статус карты...")
        self.filter_card_status.clicked.connect(lambda: print("Фильтр: статус карты"))
        
        self.filter_bonus_range = QPushButton("Баланс бонусов...")
        self.filter_bonus_range.clicked.connect(lambda: print("Фильтр: баланс бонусов"))
        
        filters_layout.addWidget(self.filter_card_type)
        filters_layout.addWidget(self.filter_card_status)
        filters_layout.addWidget(self.filter_bonus_range)
        
        left_panel.addWidget(filters_group)
        left_panel.addStretch()
        
        layout.addLayout(left_panel, 1)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Телефон", "Карта", "Статус"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.cellClicked.connect(self._on_user_cell_clicked)
        
        layout.addWidget(self.users_table, 3)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Добавить")
        self.add_user_button.clicked.connect(self._add_user)
        self.add_user_button.setEnabled(self.user_type == "admin")
        
        self.edit_user_button = QPushButton("Редактировать")
        self.edit_user_button.clicked.connect(self._edit_user)
        self.edit_user_button.setEnabled(self.user_type == "admin")
        
        self.delete_user_button = QPushButton("Удалить")
        self.delete_user_button.clicked.connect(self._delete_user)
        self.delete_user_button.setEnabled(self.user_type == "admin")
        
        actions_layout.addWidget(self.add_user_button)
        actions_layout.addWidget(self.edit_user_button)
        actions_layout.addWidget(self.delete_user_button)
        
        layout.addLayout(actions_layout)
        
        # Загрузка данных
        self._load_users()
        
        self.tab_widget.addTab(tab, "Пользователи")
    
    def _create_cards_tab(self):
        """Создание вкладки 'Карты'."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Левая панель (поиск и фильтры)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Поиск
        search_group = QGroupBox("Поиск")
        search_layout = QVBoxLayout(search_group)
        
        self.cards_search_input = QLineEdit()
        self.cards_search_input.setPlaceholderText("Номер карты или ID...")
        self.cards_search_input.textChanged.connect(self._filter_cards)
        
        self.cards_search_button = QPushButton("Найти")
        self.cards_search_button.clicked.connect(lambda: self._filter_cards(self.cards_search_input.text()))
        
        search_layout.addWidget(self.cards_search_input)
        search_layout.addWidget(self.cards_search_button)
        
        left_panel.addWidget(search_group)
        
        # Фильтры
        filters_group = QGroupBox("Фильтры")
        filters_layout = QVBoxLayout(filters_group)
        filters_layout.setSpacing(5)
        
        self.filter_card_type_cards = QPushButton("Тип карты...")
        self.filter_card_type_cards.clicked.connect(lambda: print("Фильтр: тип карты"))
        
        self.filter_card_client = QPushButton("Владелец...")
        self.filter_card_client.clicked.connect(lambda: print("Фильтр: владелец"))
        
        self.filter_card_issued = QPushButton("Дата выдачи...")
        self.filter_card_issued.clicked.connect(lambda: print("Фильтр: дата выдачи"))
        
        filters_layout.addWidget(self.filter_card_type_cards)
        filters_layout.addWidget(self.filter_card_client)
        filters_layout.addWidget(self.filter_card_issued)
        
        left_panel.addWidget(filters_group)
        left_panel.addStretch()
        
        layout.addLayout(left_panel, 1)
        
        # Таблица карт
        self.cards_table = QTableWidget()
        self.cards_table.setColumnCount(6)
        self.cards_table.setHorizontalHeaderLabels([
            "ID", "Номер", "Клиент", "Тип", "Статус", "Дата выдачи"
        ])
        self.cards_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cards_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.cards_table, 3)
        
        # Кнопки действий
        actions_layout = QHBoxLayout()
        self.add_card_button = QPushButton("Выдать карту")
        self.add_card_button.clicked.connect(self._add_card)
        
        self.activate_card_button = QPushButton("Активировать")
        self.activate_card_button.clicked.connect(self._activate_card)
        
        self.deactivate_card_button = QPushButton("Заблокировать")
        self.deactivate_card_button.clicked.connect(self._deactivate_card)
        
        actions_layout.addWidget(self.add_card_button)
        actions_layout.addWidget(self.activate_card_button)
        actions_layout.addWidget(self.deactivate_card_button)
        
        layout.addLayout(actions_layout)
        
        self._load_cards()
        
        self.tab_widget.addTab(tab, "Карты")
    
    def _create_shops_tab(self):
        """Создание вкладки 'Магазины'."""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Поиск
        search_group = QGroupBox("Поиск")
        search_layout = QVBoxLayout(search_group)
        
        self.shops_search_input = QLineEdit()
        self.shops_search_input.setPlaceholderText("Название или ID...")
        self.shops_search_input.textChanged.connect(self._filter_shops)
        
        self.shops_search_button = QPushButton("Найти")
        self.shops_search_button.clicked.connect(lambda: self._filter_shops(self.shops_search_input.text()))
        
        search_layout.addWidget(self.shops_search_input)
        search_layout.addWidget(self.shops_search_button)
        
        left_panel.addWidget(search_group)
        
        # Фильтры
        filters_group = QGroupBox("Фильтры")
        filters_layout = QVBoxLayout(filters_group)
        filters_layout.setSpacing(5)
        
        self.filter_shop_region = QPushButton("Регион...")
        self.filter_shop_region.clicked.connect(lambda: print("Фильтр: регион"))
        
        self.filter_shop_chain = QPushButton("Сеть...")
        self.filter_shop_chain.clicked.connect(lambda: print("Фильтр: сеть"))
        
        filters_layout.addWidget(self.filter_shop_region)
        filters_layout.addWidget(self.filter_shop_chain)
        
        left_panel.addWidget(filters_group)
        left_panel.addStretch()
        
        layout.addLayout(left_panel, 1)
        
        self.shops_table = QTableWidget()
        self.shops_table.setColumnCount(4)
        self.shops_table.setHorizontalHeaderLabels([
            "ID", "Название", "Адрес", "Телефон"
        ])
        self.shops_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.shops_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.shops_table, 3)
        
        actions_layout = QHBoxLayout()
        self.add_shop_button = QPushButton("Добавить магазин")
        self.add_shop_button.clicked.connect(self._add_shop)
        self.add_shop_button.setEnabled(self.user_type == "admin")
        
        self.edit_shop_button = QPushButton("Редактировать")
        self.edit_shop_button.clicked.connect(self._edit_shop)
        self.edit_shop_button.setEnabled(self.user_type == "admin")
        
        self.delete_shop_button = QPushButton("Удалить")
        self.delete_shop_button.clicked.connect(self._delete_shop)
        self.delete_shop_button.setEnabled(self.user_type == "admin")
        
        actions_layout.addWidget(self.add_shop_button)
        actions_layout.addWidget(self.edit_shop_button)
        actions_layout.addWidget(self.delete_shop_button)
        
        layout.addLayout(actions_layout)
        
        self.tab_widget.addTab(tab, "Магазины")
    
    # === Загрузка данных ===
    def _load_users(self):
        """Загрузка пользователей из API."""
        try:
            response = self.api_request("GET", "/clients")
            if response.status_code == 200:
                users = response.json()
                self._populate_users(users)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить пользователей:\n{e}")
    
    def _load_cards(self):
        """Загрузка карт из API."""
        try:
            response = self.api_request("GET", "/cards")
            if response.status_code == 200:
                cards = response.json()
                self._populate_cards(cards)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить карты:\n{e}")
    
    # === Заполнение таблиц ===
    def _populate_users(self, users: list):
        """Заполнение таблицы пользователей."""
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user.get("client_id", ""))))
            fio = f"{user.get('last_name', '')} {user.get('first_name', '')} {user.get('middle_name', '') or ''}".strip()
            self.users_table.setItem(row, 1, QTableWidgetItem(fio))
            self.users_table.setItem(row, 2, QTableWidgetItem(user.get("phone", "")))
            self.users_table.setItem(row, 3, QTableWidgetItem(""))
            self.users_table.setItem(row, 4, QTableWidgetItem(""))
    
    def _populate_cards(self, cards: list):
        """Заполнение таблицы карт."""
        self.cards_table.setRowCount(len(cards))
        for row, card in enumerate(cards):
            self.cards_table.setItem(row, 0, QTableWidgetItem(str(card.get("card_id", ""))))
            self.users_table.setItem(row, 1, QTableWidgetItem(card.get("card_number", "")))
            self.users_table.setItem(row, 2, QTableWidgetItem(str(card.get("client_id", ""))))
            card_type = card.get("card_type", {})
            self.users_table.setItem(row, 3, QTableWidgetItem(card_type.get("type_name", "")))
            status = "Активна" if card.get("is_active", False) else "Заблокирована"
            self.users_table.setItem(row, 4, QTableWidgetItem(status))
            self.users_table.setItem(row, 5, QTableWidgetItem(card.get("issue_date", "")))
    
    # === Фильтрация ===
    def _filter_users(self, text: str):
        """Фильтрация пользователей."""
        if not text:
            self._load_users()
            return
        
        # В будущем добавить фильтрацию через API
        pass
    
    def _filter_cards(self, text: str):
        """Фильтрация карт."""
        if not text:
            self._load_cards()
            return
        
        # В будущем добавить фильтрацию через API
        pass
    
    def _filter_shops(self, text: str):
        """Фильтрация магазинов."""
        if not text:
            self._load_shops()
            return
        
        # В будущем добавить фильтрацию через API
        pass
    
    # === Действия с пользователями ===
    def _add_user(self):
        """Добавление пользователя."""
        QMessageBox.information(self, "Инфо", "Функция добавления пользователя будет доступна при подключении к API")
    
    def _edit_user(self):
        """Редактирование пользователя."""
        QMessageBox.information(self, "Инфо", "Функция редактирования пользователя будет доступна при подключении к API")
    
    def _delete_user(self):
        """Удаление пользователя."""
        if QMessageBox.question(self, "Подтверждение", "Удалить выбранного пользователя?") == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Инфо", "Функция удаления пользователя будет доступна при подключении к API")
    
    # === Действия с картами ===
    def _add_card(self):
        """Выдача новой карты."""
        QMessageBox.information(self, "Инфо", "Функция выдачи карты будет доступна при подключении к API")
    
    def _activate_card(self):
        """Активация карты."""
        QMessageBox.information(self, "Инфо", "Функция активации карты будет доступна при подключении к API")
    
    def _deactivate_card(self):
        """Блокировка карты."""
        QMessageBox.information(self, "Инфо", "Функция блокировки карты будет доступна при подключении к API")
    
    # === Действия с магазинами ===
    def _add_shop(self):
        """Добавление магазина."""
        QMessageBox.information(self, "Инфо", "Функция добавления магазина будет доступна при подключении к API")
    
    def _edit_shop(self):
        """Редактирование магазина."""
        QMessageBox.information(self, "Инфо", "Функция редактирования магазина будет доступна при подключении к API")
    
    def _delete_shop(self):
        """Удаление магазина."""
        if QMessageBox.question(self, "Подтверждение", "Удалить выбранный магазин?") == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Инфо", "Функция удаления магазина будет доступна при подключении к API")
    
    def _on_user_cell_clicked(self, row: int, column: int):
        """Обработка клика по ячейке таблицы пользователей."""
        if column == 3:  # Номер карты
            card_number = self.users_table.item(row, column).text()
            print(f"Переход к карте: {card_number}")
            self.tab_widget.setCurrentIndex(1)
            self.cards_search_input.setText(card_number)
            self._filter_cards(card_number)
