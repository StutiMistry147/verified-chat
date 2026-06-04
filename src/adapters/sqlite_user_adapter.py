import sqlite3
import asyncio
import bcrypt
from typing import Optional
from ports.user_repository_port import UserRepositoryPort
from domain.user import User

class SQLiteUserAdapter(UserRepositoryPort):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None
    
    def _get_connection(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn
    
    async def get_by_username(self, username: str) -> Optional[User]:
        def _query():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, hashed_password FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return User(id=row[0], username=row[1], hashed_password=row[2])
            return None
        return await asyncio.to_thread(_query)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        def _query():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, hashed_password FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(id=row[0], username=row[1], hashed_password=row[2])
            return None
        return await asyncio.to_thread(_query)
    
    async def save(self, user: User) -> None:
        def _save():
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, username, hashed_password) VALUES (?, ?, ?)",
                (user.id, user.username, user.hashed_password)
            )
            conn.commit()
        await asyncio.to_thread(_save)
