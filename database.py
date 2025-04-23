import sqlite3
from datetime import datetime, timedelta
import os
import threading

class Database:
    def __init__(self, db_path="mental_mindscape.db"):
        # Create db directory if it doesn't exist
        dir_name = os.path.dirname(db_path)
        if dir_name:  # Only try to create directory if there is one specified
            os.makedirs(dir_name, exist_ok=True)

        # Use check_same_thread=False to allow access from multiple threads
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        # Create a lock for thread safety
        self.lock = threading.Lock()
        self.create_tables()

    def create_tables(self):
        with self.lock:
            cursor = self.conn.cursor()

            # Users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Mood entries table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mood_score REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')

            # Chat history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')

            self.conn.commit()

    def add_user(self, username, password_hash):
        with self.lock:
            cursor = self.conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                self.conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    def get_user(self, username):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def add_mood_entry(self, user_id, mood_score, notes):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO mood_entries (user_id, mood_score, notes) VALUES (?, ?, ?)",
                (user_id, mood_score, notes)
            )
            self.conn.commit()
            return cursor.lastrowid

    def get_mood_history(self, user_id, days=30):
        with self.lock:
            cursor = self.conn.cursor()
            date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            cursor.execute(
                """SELECT * FROM mood_entries
                   WHERE user_id = ? AND date(created_at) >= ?
                   ORDER BY created_at""",
                (user_id, date_limit)
            )

            results = cursor.fetchall()
            return [dict(row) for row in results] if results else []

    def add_chat_entry(self, user_id, message, response):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (user_id, message, response) VALUES (?, ?, ?)",
                (user_id, message, response)
            )
            self.conn.commit()
            return cursor.lastrowid

    def get_chat_history(self, user_id, limit=10):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )

            results = cursor.fetchall()
            return [dict(row) for row in results] if results else []

    def close(self):
        with self.lock:
            if self.conn:
                self.conn.close()
