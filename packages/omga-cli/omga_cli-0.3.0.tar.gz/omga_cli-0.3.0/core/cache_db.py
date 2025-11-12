import sqlite3
import datetime
import threading
from core.config import CACHE_DB  

_lock = threading.Lock()

def get_connection():
    conn = sqlite3.connect(CACHE_DB, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at DATETIME
    )
    ''')
    conn.commit()
    return conn

def get(key: str) -> str | None:
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM cache WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

def set_(key: str, value: str):
    with _lock:
        conn = get_connection()
        now = datetime.datetime.now()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO cache (key, value, updated_at) VALUES (?, ?, ?)
        ''', (key, value, now))
        conn.commit()
        conn.close()

# رفع warning مربوط به datetime
def adapt_datetime(val):
    return val.isoformat(" ")
sqlite3.register_adapter(datetime.datetime, adapt_datetime)