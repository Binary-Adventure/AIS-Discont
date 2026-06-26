import secrets
import string
from typing import List, Dict, Any

class ApiDatabaseManager:
    """Менеджер БД для API с проверкой прав доступа."""
    def __init__(self, db, user_type: str, user_id: int = None, key_id: int = None):
        self.db = db
        self.user_type = user_type
        self.user_id = user_id
        self.key_id = key_id
        self._permissions = self._get_permissions()

    def _get_permissions(self) -> dict:
        if self.user_type == "admin":
            return {
                "clients": {"read", "create", "update", "delete"},
                "cards": {"read", "create", "update", "delete", "activate", "deactivate"},
                "card_types": {"read", "create", "update", "delete"},
                "bonus_accounts": {"read", "create", "update", "add_bonus", "spend_bonus"},
                "transactions": {"read", "create"},
                "receipts": {"read", "create"},
                "analytics": {"read"},
                "sources": {"read", "create", "delete", "update"},
            }
        else:
            return {
                "clients": {"read"},
                "cards": {"read"},
                "card_types": {"read"},
                "bonus_accounts": {"read", "add_bonus", "spend_bonus"},
                "transactions": {"read", "create"},
                "receipts": {"read", "create"},
                "analytics": {"read"},
                "sources": {"read"},
            }

    def _check_permission(self, resource: str, action: str) -> bool:
        return action in self._permissions.get(resource, set())

    # === Clients ===
    def get_client_by_id(self, client_id: int):
        if not self._check_permission("clients", "read"):
            raise PermissionError("Нет прав на чтение клиентов")
        return self.db.get_client_by_id(client_id)

    def get_client_by_phone(self, phone: str):
        if not self._check_permission("clients", "read"):
            raise PermissionError("Нет прав на чтение клиентов")
        return self.db.get_client_by_phone(phone)

    def search_clients(self, search_text: str) -> List[Dict[str, Any]]:
        search_text = search_text.strip()
        if not search_text:
            return []
        
        with self.db._get_cursor() as cur:
            cur.execute(
                """SELECT client_id, first_name, last_name, middle_name, phone, email,
                          registration_date
                   FROM clients WHERE phone = %s;""",
                (search_text,)
            )
            result = cur.fetchone()
            if result:
                return [self._row_to_client_dict(result)]
            
            search_pattern = f"%{search_text}%"
            cur.execute(
                """SELECT client_id, first_name, last_name, middle_name, phone, email,
                          registration_date
                   FROM clients
                   WHERE (first_name ILIKE %s OR last_name ILIKE %s OR middle_name ILIKE %s)
                   ORDER BY last_name, first_name;""",
                (search_pattern, search_pattern, search_pattern)
            )
            results = cur.fetchall()
            return [self._row_to_client_dict(row) for row in results]

    def _row_to_client_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "client_id": row[0], "first_name": row[1], "last_name": row[2],
            "middle_name": row[3], "phone": row[4], "email": row[5],
            "registration_date": row[6]
        }

    def create_client(self, first_name: str, last_name: str, phone: str,
                      middle_name: str = None, email: str = None, birth_date: str = None):
        if not self._check_permission("clients", "create"):
            raise PermissionError("Нет прав на создание клиентов")
        return self.db.create_client(first_name, last_name, phone, middle_name, email, birth_date)

    def update_client(self, client_id: int, **kwargs):
        if not self._check_permission("clients", "update"):
            raise PermissionError("Нет прав на обновление клиентов")
        return self.db.update_client(client_id, **kwargs)

    def get_all_clients(self):
        if not self._check_permission("clients", "read"):
            raise PermissionError("Нет прав на чтение клиентов")
        return self.db.get_all_clients()

    def delete_client(self, client_id: int):
        if not self._check_permission("clients", "delete"):
            raise PermissionError("Нет прав на удаление клиентов")
        self.db.delete_client(client_id)

    # === Card Types ===
    def get_card_type_by_id(self, card_type_id: int):
        if not self._check_permission("card_types", "read"):
            raise PermissionError("Нет прав на чтение типов карт")
        return self.db.get_card_type_by_id(card_type_id)

    def get_all_card_types(self):
        if not self._check_permission("card_types", "read"):
            raise PermissionError("Нет прав на чтение типов карт")
        return self.db.get_all_card_types()

    def create_card_type(self, type_name: str, discount_percent: float = 0.0,
                         bonus_accrual_rate: float = 0.0, upgrade_threshold: float = 0.0):
        if not self._check_permission("card_types", "create"):
            raise PermissionError("Нет прав на создание типов карт")
        return self.db.create_card_type(type_name, discount_percent, bonus_accrual_rate, upgrade_threshold)

    def update_card_type(self, card_type_id: int, **kwargs):
        if not self._check_permission("card_types", "update"):
            raise PermissionError("Нет прав на обновление типов карт")
        return self.db.update_card_type(card_type_id, **kwargs)

    def delete_card_type(self, card_type_id: int):
        if not self._check_permission("card_types", "delete"):
            raise PermissionError("Нет прав на удаление типов карт")
        self.db.delete_card_type(card_type_id)

    # === Cards ===
    def get_card_by_id(self, card_id: int):
        if not self._check_permission("cards", "read"):
            raise PermissionError("Нет прав на чтение карт")
        return self.db.get_card_by_id(card_id)

    def get_card_by_number(self, card_number: str):
        if not self._check_permission("cards", "read"):
            raise PermissionError("Нет прав на чтение карт")
        return self.db.get_card_by_number(card_number)

    def get_cards_by_client(self, client_id: int):
        if not self._check_permission("cards", "read"):
            raise PermissionError("Нет прав на чтение карт")
        return self.db.get_cards_by_client(client_id)

    def create_card(self, client_id: int, card_number: str, card_type_id: int = None):
        if not self._check_permission("cards", "create"):
            raise PermissionError("Нет прав на создание карт")
        return self.db.create_card(client_id, card_number, card_type_id)

    def update_card(self, card_id: int, **kwargs):
        if not self._check_permission("cards", "update"):
            raise PermissionError("Нет прав на обновление карт")
        return self.db.update_card(card_id, **kwargs)

    def delete_card(self, card_id: int):
        if not self._check_permission("cards", "delete"):
            raise PermissionError("Нет прав на удаление карт")
        self.db.delete_card(card_id)

    def activate_card(self, card_id: int):
        if not self._check_permission("cards", "activate"):
            raise PermissionError("Нет прав на активацию карт")
        return self.db.activate_card(card_id)

    def deactivate_card(self, card_id: int):
        if not self._check_permission("cards", "deactivate"):
            raise PermissionError("Нет прав на деактивацию карт")
        return self.db.deactivate_card(card_id)

    # === Bonus Accounts ===
    def get_bonus_account_by_client(self, client_id: int):
        if not self._check_permission("bonus_accounts", "read"):
            raise PermissionError("Нет прав на чтение бонусных счетов")
        return self.db.get_bonus_account_by_client(client_id)

    def get_bonus_account_by_id(self, account_id: int):
        if not self._check_permission("bonus_accounts", "read"):
            raise PermissionError("Нет прав на чтение бонусных счетов")
        return self.db.get_bonus_account_by_id(account_id)

    def add_bonus(self, account_id: int, amount: float):
        if not self._check_permission("bonus_accounts", "add_bonus"):
            raise PermissionError("Нет прав на начисление бонусов")
        return self.db.add_bonus(account_id, amount)

    def spend_bonus(self, account_id: int, amount: float):
        if not self._check_permission("bonus_accounts", "spend_bonus"):
            raise PermissionError("Нет прав на списание бонусов")
        return self.db.spend_bonus(account_id, amount)

    # === Transactions ===
    def create_transaction(self, card_id: int, receipt_id: int, operation_type: str,
                           amount: float, bonuses_applied: float = 0.0):
        if not self._check_permission("transactions", "create"):
            raise PermissionError("Нет прав на создание транзакций")
        return self.db.create_transaction(card_id, receipt_id, operation_type, amount, bonuses_applied)

    def get_transactions_by_card(self, card_id: int):
        if not self._check_permission("transactions", "read"):
            raise PermissionError("Нет прав на чтение транзакций")
        return self.db.get_transactions_by_card(card_id)

    # === Receipts ===
    def create_receipt(self, card_id: int, total_amount: float,
                       total_discount_amount: float = 0.0):
        if not self._check_permission("receipts", "create"):
            raise PermissionError("Нет прав на создание чеков")
        if self.key_id is None:
            raise ValueError("Не установлен key_id для чека")
        return self.db.create_receipt(card_id, self.key_id, total_amount, total_discount_amount)

    def get_receipt_by_id(self, receipt_id: int):
        if not self._check_permission("receipts", "read"):
            raise PermissionError("Нет прав на чтение чеков")
        return self.db.get_receipt_by_id(receipt_id)

    # === Sources ===
    def get_all_sources(self) -> List[Dict[str, Any]]:
        with self.db._get_cursor() as cur:
            cur.execute("""
                SELECT ak.key_id, ak.api_key, ak.user_type, ak.user_id,
                       ak.description, ak.is_active, ak.created_at
                FROM api_keys ak
                ORDER BY ak.key_id;
            """)
            return [self._row_to_source_dict(row) for row in cur.fetchall()]

    def _row_to_source_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "key_id": row[0], "api_key": row[1], "user_type": row[2],
            "user_id": row[3], "description": row[4], "is_active": row[5],
            "created_at": row[6]
        }

    def create_source(self, user_type: str, user_id: int = None, description: str = None) -> str:
        chars = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(chars) for _ in range(64))
        with self.db._get_cursor() as cur:
            cur.execute(
                """INSERT INTO api_keys (api_key, user_type, user_id, description, is_active)
                   VALUES (%s, %s, %s, %s, %s) RETURNING key_id, api_key;""",
                (api_key, user_type, user_id, description, True)
            )
            result = cur.fetchone()
        self.db.conn.commit()
        return result[1]

    def update_source(self, key_id: int, **kwargs):
        if not self._check_permission("sources", "update"):
            raise PermissionError("Нет прав на обновление источников")
        updates, values = [], []
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = %s")
                values.append(value)
        if not updates:
            return False
        values.append(key_id)
        with self.db._get_cursor() as cur:
            cur.execute(f"UPDATE api_keys SET {', '.join(updates)} WHERE key_id = %s;", tuple(values))
        self.db.conn.commit()
        return cur.rowcount > 0

    def delete_source(self, key_id: int):
        if not self._check_permission("sources", "delete"):
            raise PermissionError("Нет прав на удаление источников")
        with self.db._get_cursor() as cur:
            cur.execute("DELETE FROM api_keys WHERE key_id = %s;", (key_id,))
        self.db.conn.commit()
        return cur.rowcount > 0