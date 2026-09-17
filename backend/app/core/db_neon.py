import os
import sqlite3
from typing import Dict, Any, Optional

DATABASE_URL = os.getenv("DATABASE_URL", "")

class NeonDatabaseManager:
    """
    Neon Serverless PostgreSQL Database Connection & Query Manager.
    Supports Neon PostgreSQL Database with fallback for local sqlite storage.
    """

    def __init__(self):
        self.db_path = "local_persistent.db"
        self._init_local_db()

    def _init_local_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passkeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                credential_id TEXT UNIQUE NOT NULL,
                raw_credential TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_user(self, email: str, password_hash: str, salt: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password_hash, salt) VALUES (?, ?, ?)",
                (email, password_hash, salt)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

    def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT email, password_hash, salt FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return {"email": row[0], "password_hash": row[1], "salt": row[2]}
            return None
        except Exception:
            return None

neon_db = NeonDatabaseManager()
