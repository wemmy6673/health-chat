import aiosqlite
import json
from datetime import datetime

DB_PATH = "health_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.commit()

async def upsert_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, datetime.utcnow().isoformat()))
        await db.commit()

async def save_message(user_id: int, role: str, content: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO conversations (user_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, role, content, datetime.utcnow().isoformat()))
        await db.commit()

async def get_conversation_history(user_id: int, limit: int = 10) -> list:
    """Fetch last N messages for a user to use as context."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT role, content FROM conversations
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        rows = await cursor.fetchall()
        # Reverse to get chronological order
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

async def clear_history(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
        await db.commit()