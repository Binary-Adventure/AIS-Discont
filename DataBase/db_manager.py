import psycopg2
import secrets
import string
from typing import List, Optional
from ..config import Config

from .models import Receipt, Transaction, Client, Card, CardType, BonusAccount

class DataBaseManager:
    """Менеджер базы данных PostgreSQL."""
    def __init__(self, config: Config):
        self.config = config
        self.conn = psycopg2.connect(
            dbname=config.db.db_name,
            user=config.db.db_user,
            password=config.db.db_pass,
            host=config.db.db_host,
            port=config.db.db_port
        )
        self.conn.autocommit = False

    def _get_cursor(self):
        return self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def init_db(self, sql_path: str = './DataBase/tables.sql'):
        with self._get_cursor() as cur:
            with open(sql_path, 'r', encoding='utf-8') as file:
                sql = file.read()
            cur.execute(sql)
        self.conn.commit()

    # === Clients ===
    def get_client_by_id(self, client_id: int) -> Optional['Client']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM clients WHERE client_id = %s;", (client_id,))
            result = cur.fetchone()
            return self._row_to_client(result) if result else None

    def get_client_by_phone(self, phone: str) -> Optional['Client']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM clients WHERE phone = %s;", (phone,))
            result = cur.fetchone()
            return self._row_to_client(result) if result else None

    def create_client(self, first_name: str, last_name: str, phone: str,
                      middle_name: str = None, email: str = None, birth_date: str = None) -> int:
        with self._get_cursor() as cur:
            cur.execute(
                """INSERT INTO clients (first_name, last_name, middle_name, phone, email, birth_date)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING client_id;""",
                (first_name, last_name, middle_name, phone, email, birth_date)
            )
            client_id = cur.fetchone()[0]
        self.conn.commit()

        try:
            self.create_bonus_account(client_id)
        except Exception as e:
            print(f"Warning: Не удалось создать бонусный счет: {e}")
        
        return client_id

    def get_all_clients(self) -> List['Client']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM clients;")
            return [self._row_to_client(row) for row in cur.fetchall()]

    def _row_to_client(self, row: tuple) -> 'Client':
        return Client(*row)

    def update_client(self, client_id: int, **kwargs):
        if not kwargs:
            return
        updates, values = [], []
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = %s")
                values.append(value)
        if updates:
            with self._get_cursor() as cur:
                cur.execute(f"UPDATE clients SET {', '.join(updates)} WHERE client_id = %s;", (*values, client_id))
            self.conn.commit()

    def delete_client(self, client_id: int):
        with self._get_cursor() as cur:
            cur.execute("DELETE FROM clients WHERE client_id = %s;", (client_id,))
        self.conn.commit()

    # === Card Types ===
    def get_card_type_by_id(self, card_type_id: int) -> Optional['CardType']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM card_types WHERE card_type_id = %s;", (card_type_id,))
            result = cur.fetchone()
            return self._row_to_card_type(result) if result else None

    def get_all_card_types(self) -> List['CardType']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM card_types;")
            return [self._row_to_card_type(row) for row in cur.fetchall()]

    def create_card_type(self, type_name: str, discount_percent: float = 0.0,
                         bonus_accrual_rate: float = 0.0, upgrade_threshold: float = 0.0) -> int:
        with self._get_cursor() as cur:
            cur.execute(
                """INSERT INTO card_types (type_name, discount_percent, bonus_accrual_rate, upgrade_threshold)
                   VALUES (%s, %s, %s, %s) RETURNING card_type_id;""",
                (type_name, discount_percent, bonus_accrual_rate, upgrade_threshold)
            )
            card_type_id = cur.fetchone()[0]
        self.conn.commit()
        return card_type_id

    def update_card_type(self, card_type_id: int, **kwargs):
        if not kwargs:
            return
        updates, values = [], []
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = %s")
                values.append(value)
        if updates:
            with self._get_cursor() as cur:
                cur.execute(f"UPDATE card_types SET {', '.join(updates)} WHERE card_type_id = %s;", (*values, card_type_id))
            self.conn.commit()

    def delete_card_type(self, card_type_id: int):
        with self._get_cursor() as cur:
            cur.execute("DELETE FROM card_types WHERE card_type_id = %s;", (card_type_id,))
        self.conn.commit()

    def _row_to_card_type(self, row: tuple) -> 'CardType':
        return CardType(card_type_id=row[0], type_name=row[1], discount_percent=row[2],
                        bonus_accrual_rate=row[3], upgrade_threshold=row[4])

    # === Cards ===
    def get_card_by_id(self, card_id: int) -> Optional['Card']:
        with self._get_cursor() as cur:
            cur.execute(
                """SELECT c.*, ct.* FROM cards c
                   LEFT JOIN card_types ct ON c.card_type_id = ct.card_type_id
                   WHERE c.card_id = %s;""", (card_id,)
            )
            result = cur.fetchone()
            return self._row_to_card(result) if result else None

    def get_card_by_number(self, card_number: str) -> Optional['Card']:
        with self._get_cursor() as cur:
            cur.execute(
                """SELECT c.*, ct.* FROM cards c
                   LEFT JOIN card_types ct ON c.card_type_id = ct.card_type_id
                   WHERE c.card_number = %s;""", (card_number,)
            )
            result = cur.fetchone()
            return self._row_to_card(result) if result else None

    def get_cards_by_client(self, client_id: int) -> List['Card']:
        with self._get_cursor() as cur:
            cur.execute(
                """SELECT c.*, ct.* FROM cards c
                   LEFT JOIN card_types ct ON c.card_type_id = ct.card_type_id
                   WHERE c.client_id = %s;""", (client_id,)
            )
            return [self._row_to_card(row) for row in cur.fetchall()]

    def create_card(self, client_id: int, card_number: str, card_type_id: int = None) -> int:
        with self._get_cursor() as cur:
            cur.execute("SELECT card_id FROM cards WHERE client_id = %s AND is_active = TRUE;", (client_id,))
            if cur.fetchone():
                raise ValueError("У клиента уже есть активная карта")
            
            cur.execute(
                """INSERT INTO cards (client_id, card_number, card_type_id, is_active)
                   VALUES (%s, %s, %s, %s) RETURNING card_id;""",
                (client_id, card_number, card_type_id, True)
            )
            card_id = cur.fetchone()[0]
        self.conn.commit()
        return card_id

    def update_card(self, card_id: int, **kwargs):
        if not kwargs:
            return
        updates, values = [], []
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = %s")
                values.append(value)
        if updates:
            with self._get_cursor() as cur:
                cur.execute(f"UPDATE cards SET {', '.join(updates)} WHERE card_id = %s;", (*values, card_id))
            self.conn.commit()

    def delete_card(self, card_id: int):
        with self._get_cursor() as cur:
            cur.execute("DELETE FROM cards WHERE card_id = %s;", (card_id,))
        self.conn.commit()

    def activate_card(self, card_id: int):
        self.update_card(card_id, is_active=True)

    def deactivate_card(self, card_id: int):
        self.update_card(card_id, is_active=False)

    def _row_to_card(self, row: tuple) -> 'Card':
        card_type = None
        if row[6] is not None:
            card_type = CardType(row[6], row[7], row[8], row[9], row[10])
        return Card(card_id=row[0], client_id=row[1], card_number=row[2],
                    card_type_id=row[3], is_active=row[4], issue_date=row[5], card_type=card_type)

    # === Bonus Accounts ===
    def get_bonus_account_by_client(self, client_id: int) -> Optional['BonusAccount']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM bonus_accounts WHERE client_id = %s;", (client_id,))
            result = cur.fetchone()
            return self._row_to_bonus_account(result) if result else None

    def get_bonus_account_by_id(self, account_id: int) -> Optional['BonusAccount']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM bonus_accounts WHERE account_id = %s;", (account_id,))
            result = cur.fetchone()
            return self._row_to_bonus_account(result) if result else None

    def create_bonus_account(self, client_id: int) -> int:
        with self._get_cursor() as cur:
            cur.execute(
                """INSERT INTO bonus_accounts (client_id, balance, blocked_balance)
                   VALUES (%s, 0.00, 0.00) RETURNING account_id;""", (client_id,)
            )
            account_id = cur.fetchone()[0]
        self.conn.commit()
        return account_id

    def add_bonus(self, account_id: int, amount: float):
        with self._get_cursor() as cur:
            cur.execute(
                """UPDATE bonus_accounts SET balance = balance + %s, last_update = CURRENT_TIMESTAMP
                   WHERE account_id = %s;""", (amount, account_id)
            )
        self.conn.commit()

    def spend_bonus(self, account_id: int, amount: float):
        with self._get_cursor() as cur:
            cur.execute(
                """UPDATE bonus_accounts SET balance = balance - %s, last_update = CURRENT_TIMESTAMP
                   WHERE account_id = %s AND balance >= %s;""", (amount, account_id, amount)
            )
            if cur.rowcount == 0:
                raise ValueError("Недостаточно бонусов")
        self.conn.commit()

    def _row_to_bonus_account(self, row: tuple) -> 'BonusAccount':
        return BonusAccount(account_id=row[0], client_id=row[1], balance=row[2],
                            blocked_balance=row[3], last_update=row[4])

    # === Transactions ===
    def create_transaction(self, card_id: int, receipt_id: int, operation_type: str,
                           amount: float, bonuses_applied: float = 0.0) -> int:
        with self._get_cursor() as cur:
            cur.execute(
                """INSERT INTO transaction_log (card_id, receipt_id, operation_type, amount, bonuses_applied)
                   VALUES (%s, %s, %s, %s, %s) RETURNING transaction_id;""",
                (card_id, receipt_id, operation_type, amount, bonuses_applied)
            )
            transaction_id = cur.fetchone()[0]
        self.conn.commit()
        return transaction_id

    def get_transactions_by_card(self, card_id: int) -> List['Transaction']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM transaction_log WHERE card_id = %s ORDER BY transaction_date DESC;", (card_id,))
            return [self._row_to_transaction(row) for row in cur.fetchall()]

    def _row_to_transaction(self, row: tuple) -> 'Transaction':
        return Transaction(transaction_id=row[0], card_id=row[1], receipt_id=row[2],
                           operation_type=row[3], amount=row[4], bonuses_applied=row[5], transaction_date=row[6])

    # === Receipts ===
    def create_receipt(self, card_id: int, key_id: int, total_amount: float,
                    total_discount_amount: float = 0.0) -> int:
        """Создать чек. key_id — ID API-ключа (сессии)."""
        with self._get_cursor() as cur:
            cur.execute(
                """INSERT INTO receipt_log 
                (card_id, key_id, total_amount, total_discount_amount)
                VALUES (%s, %s, %s, %s)
                RETURNING receipt_id;""",
                (card_id, key_id, total_amount, total_discount_amount)
            )
            receipt_id = cur.fetchone()[0]
        self.conn.commit()
        return receipt_id

    def get_receipt_by_id(self, receipt_id: int) -> Optional['Receipt']:
        with self._get_cursor() as cur:
            cur.execute("SELECT * FROM receipt_log WHERE receipt_id = %s;", (receipt_id,))
            result = cur.fetchone()
            return self._row_to_receipt(result) if result else None

    def _row_to_receipt(self, row: tuple) -> 'Receipt':
        return Receipt(
            receipt_id=row[0], card_id=row[1], total_discount_amount=row[2],
            key_id=row[3], total_amount=row[4], transaction_datetime=row[5]
        )

    # === Sources (API Keys) ===
    def create_api_key(self, user_type: str, user_id: int, description: str = None):
        chars = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(chars) for _ in range(32))
        with self._get_cursor() as cur:
            cur.execute(
                """INSERT INTO api_keys (api_key, user_type, user_id, description, is_active)
                   VALUES (%s, %s, %s, %s, %s) RETURNING key_id, api_key;""",
                (api_key, user_type, user_id, description, True)
            )
            result = cur.fetchone()
        self.conn.commit()
        return result[1]
    
    def get_total_purchases_by_client(self, client_id: int) -> float:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT COALESCE(SUM(r.total_amount), 0)
                FROM receipt_log r
                JOIN cards c ON r.card_id = c.card_id
                WHERE c.client_id = %s;
            """, (client_id,))
            result = cur.fetchone()
            return float(result[0]) if result else 0.0

    def check_and_upgrade_card(self, card_id: int) -> bool:
        with self._get_cursor() as cur:
            cur.execute("""
                SELECT c.client_id, c.card_type_id
                FROM cards c
                WHERE c.card_id = %s;
            """, (card_id,))
            result = cur.fetchone()
            
            if not result:
                return False
            
            client_id, current_card_type_id = result

            cur.execute("""
                SELECT card_type_id, upgrade_threshold
                FROM card_types
                WHERE card_type_id = %s;
            """, (current_card_type_id,))
            current_type = cur.fetchone()
            
            if not current_type:
                return False
            
            total_purchases = self.get_total_purchases_by_client(client_id)
            
            cur.execute("""
                SELECT card_type_id, upgrade_threshold
                FROM card_types
                WHERE upgrade_threshold > %s
                ORDER BY upgrade_threshold ASC
                LIMIT 1;
            """, (current_type[1],))
            
            next_type = cur.fetchone()
            
            if next_type:
                next_card_type_id, next_threshold = next_type
                
                if total_purchases >= next_threshold:
                    cur.execute("""
                        UPDATE cards 
                        SET card_type_id = %s
                        WHERE card_id = %s;
                    """, (next_card_type_id, card_id))
                    
                    self.conn.commit()
                    return True
            
            return False