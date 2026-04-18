import sqlite3
from contextlib import contextmanager
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "chat_history.db"


class ChatDatabase:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL DEFAULT 'Novo chat',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
                )
                """
            )

    def create_chat(self, title: str = "Novo chat") -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                "INSERT INTO chats (title) VALUES (?)",
                (title,),
            )
            return int(cursor.lastrowid)

    def list_chats(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM chats
                ORDER BY updated_at DESC, id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_chat(self, chat_id: int) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id, title, created_at, updated_at FROM chats WHERE id = ?",
                (chat_id,),
            ).fetchone()
        return dict(row) if row else None

    def chat_exists(self, chat_id: int) -> bool:
        return self.get_chat(chat_id) is not None

    def rename_chat(self, chat_id: int, title: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE chats
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (title, chat_id),
            )

    def delete_chat(self, chat_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
            conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))

    def add_message(self, chat_id: int, role: str, content: str) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO messages (chat_id, role, content)
                VALUES (?, ?, ?)
                """,
                (chat_id, role, content),
            )
            conn.execute(
                """
                UPDATE chats
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (chat_id,),
            )
            return int(cursor.lastrowid)

    def get_messages(self, chat_id: int) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, chat_id, role, content, created_at
                FROM messages
                WHERE chat_id = ?
                ORDER BY id ASC
                """,
                (chat_id,),
            ).fetchall()
        return [dict(row) for row in rows]
