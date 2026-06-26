from __future__ import annotations
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Literal

class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    birth_date: Optional[date] = None

class ClientResponse(BaseModel):
    client_id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    birth_date: Optional[date] = None
    registration_date: date

class CardTypeCreate(BaseModel):
    type_name: str
    discount_percent: float = 0.0
    bonus_accrual_rate: float = 0.0
    upgrade_threshold: float = 0.0

class CardTypeResponse(BaseModel):
    card_type_id: int
    type_name: str
    discount_percent: float
    bonus_accrual_rate: float
    upgrade_threshold: float

class CardCreate(BaseModel):
    client_id: int
    card_number: str
    card_type_id: Optional[int] = None

class CardResponse(BaseModel):
    card_id: int
    client_id: int
    card_number: str
    card_type_id: Optional[int] = None
    is_active: bool
    issue_date: date
    card_type: Optional[CardTypeResponse] = None

class BonusAccountResponse(BaseModel):
    account_id: int
    client_id: int
    balance: float
    blocked_balance: float
    last_update: datetime

class TransactionCreate(BaseModel):
    card_id: int
    receipt_id: Optional[int] = None
    operation_type: Literal["ACCRUAL", "SPEND", "ADD", "BLOCK", "UNBLOCK"]
    amount: float
    bonuses_applied: float = 0.0

class TransactionResponse(BaseModel):
    transaction_id: int
    card_id: int
    receipt_id: Optional[int] = None
    operation_type: str
    amount: float
    bonuses_applied: float
    transaction_date: datetime

class ReceiptCreate(BaseModel):
    card_id: int
    total_amount: float
    total_discount_amount: float = 0.0

class ReceiptResponse(BaseModel):
    receipt_id: int
    card_id: int
    total_discount_amount: float
    key_id: int
    total_amount: float
    transaction_datetime: datetime

class SourceCreate(BaseModel):
    user_type: str
    user_id: Optional[int] = None
    description: Optional[str] = None

class SourceResponse(BaseModel):
    key_id: int
    api_key: str
    user_type: str
    user_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

class AuthRequest(BaseModel):
    api_key: str

class AuthResponse(BaseModel):
    success: bool
    user_type: Optional[str] = None
    user_id: Optional[int] = None
    message: str

class SuccessResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None