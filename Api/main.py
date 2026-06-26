import traceback

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Optional, List

from Api.models import (
    AuthRequest, AuthResponse, SuccessResponse, ErrorResponse,
    ClientCreate, ClientResponse,
    CardTypeCreate, CardTypeResponse,
    CardCreate, CardResponse, BonusAccountResponse,
    TransactionCreate, TransactionResponse,
    ReceiptCreate, ReceiptResponse,
    SourceCreate, SourceResponse
)
from Api.api_db import ApiDatabaseManager
from Api.key_manager import KeyManager
from DataBase import DataBaseManager
from config import config

app = FastAPI(title="API Дисконтных Карт", version="1.0.0",
              docs_url="/docs", redoc_url="/redoc")

db_manager: Optional[DataBaseManager] = None
key_manager: Optional[KeyManager] = None

@app.on_event("startup")
async def startup_event():
    global db_manager, key_manager
    db_manager = DataBaseManager(config)
    key_manager = KeyManager(db_manager)
    try:
        key_manager.create_api_keys_table()
    except Exception as e:
        print(f"Предупреждение: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global db_manager
    if db_manager:
        db_manager.close()

def authenticate_request(api_key: str = Header(..., alias="X-API-Key")):
    global key_manager
    if not key_manager:
        raise HTTPException(status_code=500, detail="Сервер не инициализирован")
    result = key_manager.get_user_type_by_api_key(api_key)
    if not result:
        raise HTTPException(status_code=401, detail="Неверный или неактивный API ключ")
    key_id, user_type, user_id = result
    return ApiDatabaseManager(db_manager, user_type, user_id, key_id=key_id)

# === Auth ===
@app.post("/auth", response_model=AuthResponse)
async def auth(request: AuthRequest):
    global key_manager
    if not key_manager:
        return AuthResponse(success=False, message="Сервер не инициализирован")
    result = key_manager.get_user_type_by_api_key(request.api_key)
    if result:
        key_id, user_type, user_id = result
        return AuthResponse(success=True, user_type=user_type, user_id=user_id,
                            message=f"Аутентификация успешна ({user_type})")
    return AuthResponse(success=False, message="Неверный API ключ")

# === Clients ===
@app.get("/clients/{client_id}/purchases")
async def get_client_purchases(client_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    total = api_db.get_total_purchases_by_client(client_id)
    return {"client_id": client_id, "total_purchases": total}

@app.get("/clients/search", response_model=List[ClientResponse])
async def search_clients(query: str = "", api_db: ApiDatabaseManager = Depends(authenticate_request)):
    return api_db.search_clients(query)

@app.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    client = api_db.get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

@app.get("/clients/phone/{phone}", response_model=ClientResponse)
async def get_client_by_phone(phone: str, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    client = api_db.get_client_by_phone(phone)
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return client

@app.post("/clients", response_model=ClientResponse)
async def create_client(client: ClientCreate, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    client_id = api_db.create_client(
        first_name=client.first_name, last_name=client.last_name, phone=client.phone,
        middle_name=client.middle_name, email=client.email,
        birth_date=str(client.birth_date) if client.birth_date else None
    )
    return api_db.get_client_by_id(client_id)

@app.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: int, client_data: ClientCreate,
                        api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.update_client(client_id, first_name=client_data.first_name,
                         last_name=client_data.last_name, middle_name=client_data.middle_name,
                         phone=client_data.phone, email=client_data.email,
                         birth_date=str(client_data.birth_date) if client_data.birth_date else None)
    return api_db.get_client_by_id(client_id)

@app.delete("/clients/{client_id}")
async def delete_client(client_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.delete_client(client_id)
    return SuccessResponse(success=True, message="Клиент удален")

@app.get("/clients", response_model=List[ClientResponse])
async def get_all_clients(api_db: ApiDatabaseManager = Depends(authenticate_request)):
    return api_db.get_all_clients()

# === Card Types ===
@app.get("/card_types", response_model=List[CardTypeResponse])
async def get_card_types(api_db: ApiDatabaseManager = Depends(authenticate_request)):
    return api_db.get_all_card_types()

@app.post("/card_types", response_model=CardTypeResponse)
async def create_card_type(card_type: CardTypeCreate,
                           api_db: ApiDatabaseManager = Depends(authenticate_request)):
    card_type_id = api_db.create_card_type(
        type_name=card_type.type_name, discount_percent=card_type.discount_percent,
        bonus_accrual_rate=card_type.bonus_accrual_rate, upgrade_threshold=card_type.upgrade_threshold
    )
    return api_db.get_card_type_by_id(card_type_id)

@app.put("/card_types/{card_type_id}", response_model=CardTypeResponse)
async def update_card_type(card_type_id: int, card_type_data: CardTypeCreate,
                           api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.update_card_type(card_type_id, type_name=card_type_data.type_name,
                            discount_percent=card_type_data.discount_percent,
                            bonus_accrual_rate=card_type_data.bonus_accrual_rate,
                            upgrade_threshold=card_type_data.upgrade_threshold)
    return api_db.get_card_type_by_id(card_type_id)

@app.delete("/card_types/{card_type_id}")
async def delete_card_type(card_type_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.delete_card_type(card_type_id)
    return SuccessResponse(success=True, message="Тип карты удален")

# === Cards ===
@app.get("/cards/{card_id}", response_model=CardResponse)
async def get_card(card_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    card = api_db.get_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Карта не найдена")
    return card

@app.get("/cards/number/{card_number}", response_model=CardResponse)
async def get_card_by_number(card_number: str, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    card = api_db.get_card_by_number(card_number)
    if not card:
        raise HTTPException(status_code=404, detail="Карта не найдена")
    return card

@app.get("/cards", response_model=List[CardResponse])
async def get_cards_by_client(client_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    return api_db.get_cards_by_client(client_id)

@app.post("/cards", response_model=CardResponse)
async def create_card(card: CardCreate, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    card_id = api_db.create_card(card.client_id, card.card_number, card.card_type_id)
    return api_db.get_card_by_id(card_id)

@app.post("/cards/{card_id}/activate")
async def activate_card(card_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.activate_card(card_id)
    return SuccessResponse(success=True, message="Карта активирована")

@app.post("/cards/{card_id}/deactivate")
async def deactivate_card(card_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.deactivate_card(card_id)
    return SuccessResponse(success=True, message="Карта деактивирована")

@app.delete("/cards/{card_id}")
async def delete_card(card_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.delete_card(card_id)
    return SuccessResponse(success=True, message="Карта удалена")

# === Bonus Accounts ===
@app.get("/bonus_accounts/client/{client_id}", response_model=BonusAccountResponse)
async def get_bonus_account(client_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    account = api_db.get_bonus_account_by_client(client_id)
    if not account:
        raise HTTPException(status_code=404, detail="Бонусный счет не найден")
    return account

@app.post("/bonus_accounts/add")
async def add_bonus(account_id: int, amount: float, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.add_bonus(account_id, amount)
    return SuccessResponse(success=True, message=f"Начислено {amount} бонусов")

@app.post("/bonus_accounts/spend")
async def spend_bonus(account_id: int, amount: float, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    try:
        api_db.spend_bonus(account_id, amount)
        return SuccessResponse(success=True, message=f"Списано {amount} бонусов")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# === Transactions ===
@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(tx: TransactionCreate, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.create_transaction(
        card_id=tx.card_id, receipt_id=tx.receipt_id, operation_type=tx.operation_type,
        amount=tx.amount, bonuses_applied=tx.bonuses_applied
    )
    transactions = api_db.get_transactions_by_card(tx.card_id)
    return transactions[0] if transactions else None

@app.get("/transactions/card/{card_id}", response_model=List[TransactionResponse])
async def get_transactions(card_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    return api_db.get_transactions_by_card(card_id)

# === Receipts ===
@app.post("/receipts", response_model=ReceiptResponse)
async def create_receipt(receipt: ReceiptCreate, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    receipt_id = api_db.create_receipt(
        card_id=receipt.card_id,
        total_amount=receipt.total_amount,
        total_discount_amount=receipt.total_discount_amount
    )
    return api_db.get_receipt_by_id(receipt_id)

@app.get("/receipts/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(receipt_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    receipt = api_db.get_receipt_by_id(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Чек не найден")
    return receipt

# === Sources (API Keys) ===
@app.get("/sources", response_model=List[SourceResponse])
async def get_sources(api_db: ApiDatabaseManager = Depends(authenticate_request)):
    return api_db.get_all_sources()

@app.post("/sources", response_model=SourceResponse)
async def create_source(source: SourceCreate, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_key = api_db.create_source(
        user_type=source.user_type, user_id=source.user_id, description=source.description
    )
    sources = api_db.get_all_sources()
    return sources[-1] if sources else None

@app.put("/sources/{key_id}")
async def update_source(key_id: int, is_active: bool,
                        api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.update_source(key_id, is_active=is_active)
    return SuccessResponse(success=True, message="Источник обновлен")

@app.delete("/sources/{key_id}")
async def delete_source(key_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    api_db.delete_source(key_id)
    return SuccessResponse(success=True, message="Источник удален")


@app.get("/cards/{card_id}/check-upgrade")
async def check_card_upgrade(card_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    """Проверить и выполнить апгрейд карты."""
    upgraded = api_db.check_and_upgrade_card(card_id)
    if upgraded:
        return SuccessResponse(success=True, message="Карта повышена!")
    return SuccessResponse(success=True, message="Апгрейд не требуется")

@app.get("/clients/{client_id}/purchases")
async def get_client_purchases(client_id: int, api_db: ApiDatabaseManager = Depends(authenticate_request)):
    total = api_db.get_total_purchases_by_client(client_id)
    return {"client_id": client_id, "total_purchases": total}



# === Exception Handler ===
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    print(f"ERROR: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error=str(exc), details=str(type(exc).__name__)).model_dump()
    )