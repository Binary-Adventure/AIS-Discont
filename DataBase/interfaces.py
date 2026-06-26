from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from .models import Transaction, Client, Card, CardType, BonusAccount

class DataBaseManagerInterface(ABC):
    """Интерфейс для управления базой данных."""
    @abstractmethod
    def __init__(self, config): pass

    @abstractmethod
    def close(self): pass

    @abstractmethod
    def init_db(self, sql_path: str): pass

    # === Clients ===
    @abstractmethod
    def get_client_by_id(self, client_id: int) -> Optional['Client']: pass

    @abstractmethod
    def get_client_by_phone(self, phone: str) -> Optional['Client']: pass

    @abstractmethod
    def create_client(self, first_name: str, last_name: str, phone: str,
                      middle_name: str = None, email: str = None, birth_date: str = None) -> int: pass

    @abstractmethod
    def get_all_clients(self) -> List['Client']: pass

    @abstractmethod
    def update_client(self, client_id: int, **kwargs): pass

    @abstractmethod
    def delete_client(self, client_id: int): pass

    # === Card Types ===
    @abstractmethod
    def get_card_type_by_id(self, card_type_id: int) -> Optional['CardType']: pass

    @abstractmethod
    def get_all_card_types(self) -> List['CardType']: pass

    @abstractmethod
    def create_card_type(self, type_name: str, discount_percent: float = 0.0,
                         bonus_accrual_rate: float = 0.0, upgrade_threshold: float = 0.0) -> int: pass

    @abstractmethod
    def update_card_type(self, card_type_id: int, **kwargs): pass

    @abstractmethod
    def delete_card_type(self, card_type_id: int): pass

    # === Cards ===
    @abstractmethod
    def get_card_by_id(self, card_id: int) -> Optional['Card']: pass

    @abstractmethod
    def get_card_by_number(self, card_number: str) -> Optional['Card']: pass

    @abstractmethod
    def get_cards_by_client(self, client_id: int) -> List['Card']: pass

    @abstractmethod
    def create_card(self, client_id: int, card_number: str, card_type_id: int = None) -> int: pass

    @abstractmethod
    def update_card(self, card_id: int, **kwargs): pass

    @abstractmethod
    def delete_card(self, card_id: int): pass

    @abstractmethod
    def activate_card(self, card_id: int): pass

    @abstractmethod
    def deactivate_card(self, card_id: int): pass

    # === Bonus Accounts ===
    @abstractmethod
    def get_bonus_account_by_client(self, client_id: int) -> Optional['BonusAccount']: pass

    @abstractmethod
    def create_bonus_account(self, client_id: int) -> int: pass

    @abstractmethod
    def add_bonus(self, account_id: int, amount: float): pass

    @abstractmethod
    def spend_bonus(self, account_id: int, amount: float): pass

    # === Transactions & Receipts ===
    @abstractmethod
    def create_transaction(self, card_id: int, receipt_id: int, operation_type: str,
                           amount: float, bonuses_applied: float = 0.0) -> int: pass

    @abstractmethod
    def get_transactions_by_card(self, card_id: int) -> List['Transaction']: pass

    @abstractmethod
    def create_receipt(self, card_id: int, store_id: int, total_amount: float,
                       total_discount_amount: float = 0.0) -> int: pass

    # === API Keys ===
    @abstractmethod
    def create_api_key(self, user_type: str, user_id: int, description: str = None) -> str: pass

    @abstractmethod
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]: pass