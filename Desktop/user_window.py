from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLineEdit, QPushButton, QTableWidget, QHeaderView,
    QTableWidgetItem, QLabel, QGroupBox, QMessageBox, QDoubleSpinBox
)
from ..Desktop.base_window import BaseWindow


class UserWindow(BaseWindow):
    """Окно пользователя (кассир)."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.setWindowTitle("Система дисконтных карт - Кассир")
        self.setGeometry(100, 100, 1000, 700)
        
        self.current_card = None
        self.current_client = None
        
        self.setup_ui()

    def setup_ui(self):
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        self._create_search_tab()
        self._create_transaction_tab()
        self._create_history_tab()

    # ==================== ВКЛАДКА ПОИСК КЛИЕНТА ====================
    def _create_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        search_group = QGroupBox("Поиск клиента")
        search_layout = QVBoxLayout(search_group)
        
        hint = QLabel("Можно вводить номер карты, телефон или ФИО (полностью или частично)")
        hint.setStyleSheet("color: gray; font-size: 11px;")
        search_layout.addWidget(hint)
        
        input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ФИО, телефон или номер карты...")
        input_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self._search_client)
        input_layout.addWidget(search_btn)
        
        self.search_input.returnPressed.connect(self._search_client)
        search_layout.addLayout(input_layout)
        layout.addWidget(search_group)
        
        self.client_info_group = QGroupBox("Информация о клиенте")
        self.client_info_group.setVisible(False)
        client_layout = QVBoxLayout(self.client_info_group)
        
        self.client_info_label = QLabel()
        self.client_info_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 13px;
                padding: 10px;
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        self.client_info_label.setWordWrap(True)
        client_layout.addWidget(self.client_info_label)
        
        layout.addWidget(self.client_info_group)
        
        self.card_info_group = QGroupBox("Информация о карте")
        self.card_info_group.setVisible(False)
        card_layout = QVBoxLayout(self.card_info_group)
        
        self.card_info_label = QLabel()
        self.card_info_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 13px;
                padding: 10px;
                background-color: #e8f5e9;
                border: 1px solid #a5d6a7;
                border-radius: 4px;
            }
        """)
        self.card_info_label.setWordWrap(True)
        card_layout.addWidget(self.card_info_label)
        layout.addWidget(self.card_info_group)
        
        actions_layout = QHBoxLayout()
        
        self.to_transaction_btn = QPushButton("Перейти к операции")
        self.to_transaction_btn.setMinimumHeight(40)
        self.to_transaction_btn.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.to_transaction_btn.clicked.connect(self._go_to_transaction)
        self.to_transaction_btn.setEnabled(False)
        actions_layout.addWidget(self.to_transaction_btn)
        
        layout.addLayout(actions_layout)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Поиск клиента")

    def _search_client(self):
        text = self.search_input.text().strip()
        if not text:
            self.show_warning("Ошибка", "Введите данные для поиска")
            return
        
        self.current_card = None
        self.current_client = None
        self.client_info_group.setVisible(False)
        self.card_info_group.setVisible(False)
        self.to_transaction_btn.setEnabled(False)
        
        clean_text = text.replace(" ", "").replace("-", "")
        if clean_text.isdigit() and len(clean_text) == 16:
            card = self.api_request("GET", f"/cards/number/{clean_text}")
            if card:
                self.current_card = card
                self._display_card_info(card)
                client = self.api_request("GET", f"/clients/{card.get('client_id')}")
                if client:
                    self.current_client = client
                    self._display_client_info(client)
                self.to_transaction_btn.setEnabled(True)
            else:
                self.show_info("Инфо", "Карта не найдена")
            return

        try:
            response = self.api_request("GET", f"/clients/search?query={text}")
            clients = response or []
            if not clients:
                self.show_info("Инфо", "Клиент не найден")
                return
            
            client = clients[0]
            self.current_client = client
            self._display_client_info(client)
            
            cards = self.api_request("GET", f"/cards?client_id={client.get('client_id')}")
            if cards:
                active_card = next((c for c in cards if c.get("is_active")), None)
                if active_card:
                    self.current_card = active_card
                    self._display_card_info(active_card)
                    self.to_transaction_btn.setEnabled(True)
                else:
                    self.show_warning("Внимание", "У клиента нет активных карт")
        except Exception as e:
            self.show_error("Ошибка поиска", str(e))

    def _display_client_info(self, client):
        self.client_info_group.setVisible(True)
        info = f"""
        <b>ФИО:</b> {client.get('last_name', '')} {client.get('first_name', '')} {client.get('middle_name', '') or ''}<br>
        <b>Телефон:</b> {client.get('phone', '')}<br>
        <b>Email:</b> {client.get('email', '') or 'Не указан'}<br>
        <b>Дата рождения:</b> {client.get('birth_date', '') or 'Не указана'}
        """
        self.client_info_label.setText(info)
        # ИСПРАВЛЕНО: белый текст на светлом фоне
        self.client_info_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 13px;
                padding: 10px;
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)

    def _display_card_info(self, card):
        self.card_info_group.setVisible(True)
        card_type = card.get("card_type", {})
        status = "Активна" if card.get("is_active") else "Заблокирована"
        
        account = self.api_request("GET", f"/bonus_accounts/client/{card.get('client_id')}")
        balance = account.get("balance", 0) if account else 0
        
        info = f"""
        <b>Номер карты:</b> {card.get('card_number', '')}<br>
        <b>Тип:</b> {card_type.get('type_name', 'Не указан')}<br>
        <b>Скидка:</b> {card_type.get('discount_percent', 0)}%<br>
        <b>Бонусы:</b> {card_type.get('bonus_accrual_rate', 0)}%<br>
        <b>Статус:</b> {status}<br>
        <b>Баланс бонусов:</b> {balance:.2f}
        """
        self.card_info_label.setText(info)
        self.card_info_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 13px;
                padding: 10px;
                background-color: #e8f5e9;
                border: 1px solid #a5d6a7;
                border-radius: 4px;
            }
        """)

    def _go_to_transaction(self):
        if self.current_card:
            self.tab_widget.setCurrentIndex(1)
            self.transaction_tab.set_card_data(self.current_card, self.current_client)

    # ==================== ВКЛАДКА ТРАНЗАКЦИЯ ====================
    def _create_transaction_tab(self):
        self.transaction_tab = TransactionTab(self)
        self.tab_widget.addTab(self.transaction_tab, " Операция")

    # ==================== ВКЛАДКА ИСТОРИЯ ====================
    def _create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        search_layout = QHBoxLayout()
        self.history_card_input = QLineEdit()
        self.history_card_input.setPlaceholderText("Введите номер карты...")
        search_layout.addWidget(self.history_card_input)
        
        history_search_btn = QPushButton("Показать историю")
        history_search_btn.clicked.connect(self._load_transaction_history)
        search_layout.addWidget(history_search_btn)
        layout.addLayout(search_layout)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Дата", "Тип операции", "Сумма", "Бонусы", "ID транзакции"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        header = self.history_table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.sortIndicatorChanged.connect(lambda col, order: self.history_table.sortByColumn(col, order))
        
        layout.addWidget(self.history_table)
        self.tab_widget.addTab(tab, "📋 История операций")

    def _load_transaction_history(self):
        card_number = self.history_card_input.text().strip().replace(" ", "")
        if not card_number:
            self.show_warning("Ошибка", "Введите номер карты")
            return
        
        card = self.api_request("GET", f"/cards/number/{card_number}")
        if not card:
            self.show_info("Инфо", "Карта не найдена")
            return
        
        transactions = self.api_request("GET", f"/transactions/card/{card.get('card_id')}")
        if not transactions:
            self.history_table.setRowCount(0)
            self.show_info("Инфо", "История операций пуста")
            return
        
        self.history_table.setRowCount(len(transactions))
        for row, tx in enumerate(transactions):
            date_str = str(tx.get("transaction_date", ""))[:19]
            self.history_table.setItem(row, 0, QTableWidgetItem(date_str))
            self.history_table.setItem(row, 1, QTableWidgetItem(tx.get("operation_type", "")))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{tx.get('amount', 0):.2f}"))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{tx.get('bonuses_applied', 0):.2f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(str(tx.get("transaction_id", ""))))

class TransactionTab(QWidget):
    """Вкладка для проведения транзакции."""
    
    def __init__(self, parent: UserWindow):
        super().__init__()
        self.parent_window = parent
        self.current_card = None
        self.current_client = None
        
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        self.card_info_label = QLabel("Выберите клиента на вкладке поиска")
        self.card_info_label.setStyleSheet("font-size: 12px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(self.card_info_label)
        
        amount_group = QGroupBox("Сумма покупки")
        amount_layout = QHBoxLayout(amount_group)
        
        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(0, 1000000)
        self.amount_spinbox.setDecimals(2)
        self.amount_spinbox.setPrefix("₽ ")
        self.amount_spinbox.setMinimumHeight(40)
        self.amount_spinbox.setStyleSheet("font-size: 14px;")
        amount_layout.addWidget(self.amount_spinbox)
        
        layout.addWidget(amount_group)
        
        calculation_group = QGroupBox("Расчет")
        calculation_layout = QVBoxLayout(calculation_group)
        
        self.discount_label = QLabel("Скидка: 0.00 ₽")
        self.discount_label.setStyleSheet("font-size: 12px;")
        calculation_layout.addWidget(self.discount_label)
        
        self.bonuses_label = QLabel("Бонусы к начислению: 0.00")
        self.bonuses_label.setStyleSheet("font-size: 12px;")
        calculation_layout.addWidget(self.bonuses_label)
        
        self.available_bonuses_label = QLabel("Доступно бонусов: 0.00")
        self.available_bonuses_label.setStyleSheet("font-size: 12px;")
        calculation_layout.addWidget(self.available_bonuses_label)
        
        self.use_bonuses_spinbox = QDoubleSpinBox()
        self.use_bonuses_spinbox.setRange(0, 1000000)
        self.use_bonuses_spinbox.setDecimals(2)
        self.use_bonuses_spinbox.setPrefix("Использовать бонусов: ")
        self.use_bonuses_spinbox.setMinimumHeight(35)
        calculation_layout.addWidget(self.use_bonuses_spinbox)
        
        self.total_label = QLabel("Итого к оплате: 0.00 ₽")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        calculation_layout.addWidget(self.total_label)
        
        layout.addWidget(calculation_group)
        
        actions_layout = QHBoxLayout()
        
        self.calculate_btn = QPushButton("Рассчитать")
        self.calculate_btn.setMinimumHeight(40)
        self.calculate_btn.clicked.connect(self._calculate)
        actions_layout.addWidget(self.calculate_btn)
        
        self.complete_btn = QPushButton("Завершить операцию")
        self.complete_btn.setMinimumHeight(40)
        self.complete_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        self.complete_btn.clicked.connect(self._complete_transaction)
        self.complete_btn.setEnabled(False)
        actions_layout.addWidget(self.complete_btn)
        
        layout.addLayout(actions_layout)
        
        layout.addStretch()

        self.amount_spinbox.valueChanged.connect(self._calculate)
        self.use_bonuses_spinbox.valueChanged.connect(self._calculate)

    def set_card_data(self, card, client):
        self.current_card = card
        self.current_client = client
        
        card_type = card.get("card_type", {})
        status = "Активна" if card.get("is_active") else "Заблокирована"
        
        account = self.parent_window.api_request("GET", f"/bonus_accounts/client/{card.get('client_id')}")
        balance = account.get("balance", 0) if account else 0
        
        info = f"""
        <b>Клиент:</b> {client.get('last_name', '')} {client.get('first_name', '')}<br>
        <b>Карта:</b> {card.get('card_number', '')} | {card_type.get('type_name', '')} | {status}<br>
        <b>Баланс бонусов:</b> {balance:.2f}
        """
        self.card_info_label.setText(info)

        self.card_info_label.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 12px;
                padding: 10px;
                background-color: #e8f4fc;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        
        max_bonuses = balance * 0.5
        self.use_bonuses_spinbox.setRange(0, max_bonuses)
        self.use_bonuses_spinbox.setValue(0)
        self.available_bonuses_label.setText(f"Доступно бонусов: {balance:.2f} (можно использовать до {max_bonuses:.2f})")
        
        self.complete_btn.setEnabled(True)

    def _calculate(self):
        if not self.current_card:
            return
        
        amount = self.amount_spinbox.value()
        card_type = self.current_card.get("card_type", {})
        discount_percent = card_type.get("discount_percent", 0)
        bonus_rate = card_type.get("bonus_accrual_rate", 0)

        discount_amount = amount * (discount_percent / 100)
        self.discount_label.setText(f"Скидка: {discount_amount:.2f} ₽ ({discount_percent}%)")
        
        amount_after_discount = amount - discount_amount
        bonuses_to_add = amount_after_discount * (bonus_rate / 100)
        self.bonuses_label.setText(f"Бонусы к начислению: {bonuses_to_add:.2f}")
        
        used_bonuses = self.use_bonuses_spinbox.value()
        total = amount_after_discount - used_bonuses
        self.total_label.setText(f"Итого к оплате: {total:.2f} ₽")

    def _complete_transaction(self):
        if not self.current_card:
            self.parent_window.show_warning("Ошибка", "Карта не выбрана")
            return
        
        amount = self.amount_spinbox.value()
        if amount <= 0:
            self.parent_window.show_warning("Ошибка", "Сумма покупки должна быть больше 0")
            return
        
        card_type = self.current_card.get("card_type", {})
        discount_percent = card_type.get("discount_percent", 0)
        bonus_rate = card_type.get("bonus_accrual_rate", 0)
        
        discount_amount = amount * (discount_percent / 100)
        amount_after_discount = amount - discount_amount
        bonuses_to_add = amount_after_discount * (bonus_rate / 100)
        used_bonuses = self.use_bonuses_spinbox.value()
        
        try:
            receipt = self.parent_window.api_request(
                "POST", "/receipts",
                json={
                    "card_id": self.current_card.get("card_id"),
                    "total_amount": amount,
                    "total_discount_amount": discount_amount
                }
            )
            if not receipt:
                raise Exception("Не удалось создать чек")
            receipt_id = receipt.get("receipt_id")
            
            if discount_amount > 0:
                self.parent_window.api_request(
                    "POST", "/transactions",
                    json={
                        "card_id": self.current_card.get("card_id"),
                        "receipt_id": receipt_id,
                        "operation_type": "ADD",
                        "amount": discount_amount,
                        "bonuses_applied": 0
                    }
                )
            
            if bonuses_to_add > 0:
                account = self.parent_window.api_request(
                    "GET", f"/bonus_accounts/client/{self.current_card.get('client_id')}"
                )
                if account:
                    self.parent_window.api_request(
                        "POST", f"/bonus_accounts/add?account_id={account.get('account_id')}&amount={bonuses_to_add}"
                    )
                    self.parent_window.api_request(
                        "POST", "/transactions",
                        json={
                            "card_id": self.current_card.get("card_id"),
                            "receipt_id": receipt_id,
                            "operation_type": "ACCRUAL",
                            "amount": bonuses_to_add,
                            "bonuses_applied": 0
                        }
                    )
            
            if used_bonuses > 0:
                account = self.parent_window.api_request(
                    "GET", f"/bonus_accounts/client/{self.current_card.get('client_id')}"
                )
                if account:
                    self.parent_window.api_request(
                        "POST", f"/bonus_accounts/spend?account_id={account.get('account_id')}&amount={used_bonuses}"
                    )
                    self.parent_window.api_request(
                        "POST", "/transactions",
                        json={
                            "card_id": self.current_card.get("card_id"),
                            "receipt_id": receipt_id,
                            "operation_type": "SPEND",
                            "amount": used_bonuses,
                            "bonuses_applied": used_bonuses
                        }
                    )
            
            try:
                updated_card = self.parent_window.api_request(
                    "GET", f"/cards/{self.current_card.get('card_id')}"
                )
                if updated_card and updated_card.get('card_type_id') != self.current_card.get('card_type_id'):
                    QMessageBox.information(
                        self.parent_window,
                        "Апгрейд карты!",
                        f"Поздравляем! Карта клиента автоматически повышена до уровня "
                        f"'{updated_card.get('card_type', {}).get('type_name', '')}'!"
                    )
                    self.current_card = updated_card
            except Exception as e:
                print(f"Ошибка при проверке апгрейда: {e}")
            
            total = amount_after_discount - used_bonuses
            msg = f"""
    Операция завершена успешно!

    Сумма покупки: {amount:.2f} ₽
    Скидка: {discount_amount:.2f} ₽
    Начислено бонусов: {bonuses_to_add:.2f}
    Использовано бонусов: {used_bonuses:.2f}
    Итого к оплате: {total:.2f} ₽

    ID чека: {receipt_id}
    """
            self.parent_window.show_info("Успех", msg)
            
            self.amount_spinbox.setValue(0)
            self.use_bonuses_spinbox.setValue(0)
            self._calculate()
            
        except Exception as e:
            self.parent_window.show_error("Ошибка", f"Не удалось завершить операцию:\n{e}")