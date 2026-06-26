from typing import Optional, Tuple
import secrets
import string

class KeyManager:
    def __init__(self, db):
        self.db = db

    def get_user_type_by_api_key(self, api_key: str) -> Optional[Tuple[int, str, int]]:
        """Возвращает (key_id, user_type, user_id) или None."""
        with self.db._get_cursor() as cur:
            cur.execute(
                """SELECT key_id, api_key, user_type, user_id, is_active
                   FROM api_keys WHERE api_key = %s AND is_active = TRUE;""",
                (api_key,)
            )
            result = cur.fetchone()
            if result:
                key_id, db_key, user_type, user_id, is_active = result
                if db_key == api_key:
                    return (key_id, user_type, user_id)
        return None

    def create_api_keys_table(self):
        with self.db._get_cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_id SERIAL PRIMARY KEY,
                    api_key VARCHAR(64) UNIQUE NOT NULL,
                    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('admin', 'user')),
                    user_id INTEGER,
                    description VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        self.db.conn.commit()
    
    def create_admin_key(self, description: str = None) -> str:
        """Создать API ключ для администратора."""
        with self.db._get_cursor() as cur:
            cur.execute("SELECT key_id FROM api_keys WHERE user_type = 'admin' AND is_active = TRUE;")
            if cur.fetchone():
                raise ValueError("Админ-ключ уже существует. Удалите старый ключ перед созданием нового.")
        
        chars = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(chars) for _ in range(64))
        
        with self.db._get_cursor() as cur:
            cur.execute(
                """INSERT INTO api_keys (api_key, user_type, user_id, description, is_active)
                VALUES (%s, %s, %s, %s, %s) RETURNING key_id;""",
                (api_key, "admin", None, description, True)
            )
            cur.fetchone()
        
        self.db.conn.commit()
        return api_key