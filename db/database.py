import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "knowledge.db"

def init_db():
    Path(DB_PATH).parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES categories (id)
        )
        """)
        conn.commit()

def get_connection():
    return sqlite3.connect(DB_PATH)