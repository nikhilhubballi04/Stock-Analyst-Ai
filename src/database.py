import sqlite3
from pathlib import Path
import bcrypt

DB_PATH = Path(__file__).parent.parent / "data" / "market_data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)

def init_users_table():
    """Creates the users table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def create_user(email: str, name: str, password: str) -> tuple[bool, str]:
    """Create a new user. Returns (success, message)."""
    email = email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return False, "An account with this email already exists."

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    cursor.execute(
        "INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)",
        (email, name, password_hash)
    )
    conn.commit()
    conn.close()
    return True, "Account created successfully."


def verify_user(email: str, password: str) -> tuple[bool, str]:
    """Verify login credentials. Returns (success, name_or_error_message)."""
    email = email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, password_hash FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "No account found with this email."

    name, stored_hash = row
    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return True, name
    return False, "Incorrect password."


def init_db():
    """Creates the table if it doesn't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_data (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            rsi REAL,
            macd REAL,
            macd_signal REAL,
            ma_20 REAL,
            ma_50 REAL,
            PRIMARY KEY (ticker, date)
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database ready at {DB_PATH}")


def save_data(df, ticker):
    """Insert or update rows for a ticker."""
    conn = get_connection()
    df = df.copy()
    df["ticker"] = ticker
    df.to_sql("price_data_temp", conn, if_exists="replace", index=False)

    conn.execute("""
        INSERT OR REPLACE INTO price_data
        SELECT ticker, date, open, high, low, close, volume, rsi, macd, macd_signal, ma_20, ma_50
        FROM price_data_temp
    """)
    conn.commit()
    conn.close()


def load_data(ticker):
    """Load stored data for a ticker as a DataFrame."""
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM price_data WHERE ticker = ? ORDER BY date",
        conn, params=(ticker,)
    )
    conn.close()
    return df