CREATE TABLE IF NOT EXISTS Clients (
    client_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    birth_date DATE,
    registration_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS Card_Types (
    card_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    bonus_accrual_rate DECIMAL(5,2) DEFAULT 0.00,
    upgrade_threshold DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE IF NOT EXISTS Cards (
    card_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    card_number VARCHAR(50) UNIQUE NOT NULL,
    card_type_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    issue_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE CASCADE,
    FOREIGN KEY (card_type_id) REFERENCES Card_Types(card_type_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Bonus_Accounts (
    account_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL UNIQUE,
    balance DECIMAL(10,2) DEFAULT 0.00,
    blocked_balance DECIMAL(10,2) DEFAULT 0.00,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS api_keys (
    key_id SERIAL PRIMARY KEY,
    api_key VARCHAR(64) UNIQUE NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('admin', 'user')),
    user_id INTEGER,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Receipt_Log (
    receipt_id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL,
    total_discount_amount DECIMAL(10,2) DEFAULT 0.00,
    key_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    transaction_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES Cards(card_id) ON DELETE CASCADE,
    FOREIGN KEY (key_id) REFERENCES api_keys(key_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Transaction_Log (
    transaction_id SERIAL PRIMARY KEY,
    card_id INTEGER NOT NULL,
    receipt_id INTEGER,
    operation_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    bonuses_applied DECIMAL(10,2) DEFAULT 0.00,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES Cards(card_id) ON DELETE CASCADE,
    FOREIGN KEY (receipt_id) REFERENCES Receipt_Log(receipt_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_cards_client_id ON Cards(client_id);
CREATE INDEX IF NOT EXISTS idx_cards_card_type_id ON Cards(card_type_id);
CREATE INDEX IF NOT EXISTS idx_transaction_log_card_id ON Transaction_Log(card_id);
CREATE INDEX IF NOT EXISTS idx_transaction_log_transaction_date ON Transaction_Log(transaction_date);
CREATE INDEX IF NOT EXISTS idx_receipt_log_card_id ON Receipt_Log(card_id);
CREATE INDEX IF NOT EXISTS idx_receipt_log_key_id ON Receipt_Log(key_id);
CREATE INDEX IF NOT EXISTS idx_bonus_accounts_client_id ON Bonus_Accounts(client_id);
CREATE INDEX IF NOT EXISTS idx_clients_phone ON Clients(phone);
CREATE INDEX IF NOT EXISTS idx_clients_email ON Clients(email);