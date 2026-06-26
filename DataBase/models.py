from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

@dataclass
class Client:
    client_id: int
    first_name: str
    last_name: str
    middle_name: str | None
    phone: str
    email: str | None
    birth_date: date | None
    registration_date: date

@dataclass
class CardType:
    card_type_id: int
    type_name: str
    discount_percent: Decimal
    bonus_accrual_rate: Decimal
    upgrade_threshold: Decimal

@dataclass
class Card:
    card_id: int
    client_id: int
    card_number: str
    card_type_id: int | None
    is_active: bool
    issue_date: date
    card_type: CardType | None = None

@dataclass
class BonusAccount:
    account_id: int
    client_id: int
    balance: Decimal
    blocked_balance: Decimal
    last_update: datetime

@dataclass
class Transaction:
    transaction_id: int
    card_id: int
    receipt_id: int | None
    operation_type: str
    amount: Decimal
    bonuses_applied: Decimal
    transaction_date: datetime

@dataclass
class Receipt:
    """Чек операции. key_id — ID API-ключа (сессии), с которой проведена операция."""
    receipt_id: int
    card_id: int
    total_discount_amount: Decimal
    key_id: int
    total_amount: Decimal
    transaction_datetime: datetime
