import psycopg2
import sqlite3
import os
from psycopg2.extras import RealDictCursor

def migrate_from_postgres_to_sqlite(pg_conn_string, sqlite_db_path="mental_mindscape.db"):
    """
    Migrate data from PostgreSQL to SQLite
    
    Args:
        pg_conn_string: PostgreSQL connection string
        sqlite_db_path: Path to SQLite database file
    """
    print("Starting migration from PostgreSQL to SQLite...")
    
    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(pg_conn_string)
        pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)
        print("Connected to PostgreSQL database")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return
    
    # Connect to SQLite
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)
        
        # Remove existing SQLite database if it exists
        if os.path.exists(sqlite_db_path):
            os.remove(sqlite_db_path)
            
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        print("Connected to SQLite database")
    except Exception as e:
        print(f"Error setting up SQLite: {e}")
        pg_conn.close()
        return
    
    # Create SQLite tables
    try:
        # Users table
        sqlite_cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Mood entries table
        sqlite_cursor.execute('''
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
        sqlite_cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        sqlite_conn.commit()
        print("Created SQLite tables")
    except Exception as e:
        print(f"Error creating SQLite tables: {e}")
        pg_conn.close()
        sqlite_conn.close()
        return
    
    # Migrate users
    try:
        pg_cursor.execute("SELECT * FROM users")
        users = pg_cursor.fetchall()
        
        for user in users:
            sqlite_cursor.execute(
                "INSERT INTO users (id, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (user['id'], user['username'], user['password_hash'], user['created_at'])
            )
        
        print(f"Migrated {len(users)} users")
    except Exception as e:
        print(f"Error migrating users: {e}")
    
    # Migrate mood entries
    try:
        pg_cursor.execute("SELECT * FROM mood_entries")
        mood_entries = pg_cursor.fetchall()
        
        for entry in mood_entries:
            sqlite_cursor.execute(
                "INSERT INTO mood_entries (id, user_id, mood_score, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (entry['id'], entry['user_id'], entry['mood_score'], entry['notes'], entry['created_at'])
            )
        
        print(f"Migrated {len(mood_entries)} mood entries")
    except Exception as e:
        print(f"Error migrating mood entries: {e}")
    
    # Migrate chat history
    try:
        pg_cursor.execute("SELECT * FROM chat_history")
        chat_entries = pg_cursor.fetchall()
        
        for entry in chat_entries:
            sqlite_cursor.execute(
                "INSERT INTO chat_history (id, user_id, message, response, created_at) VALUES (?, ?, ?, ?, ?)",
                (entry['id'], entry['user_id'], entry['message'], entry['response'], entry['created_at'])
            )
        
        print(f"Migrated {len(chat_entries)} chat entries")
    except Exception as e:
        print(f"Error migrating chat history: {e}")
    
    # Commit changes and close connections
    sqlite_conn.commit()
    pg_conn.close()
    sqlite_conn.close()
    
    print("Migration completed successfully")

if __name__ == "__main__":
    # Example usage
    pg_conn_string = input("Enter PostgreSQL connection string: ")
    migrate_from_postgres_to_sqlite(pg_conn_string)