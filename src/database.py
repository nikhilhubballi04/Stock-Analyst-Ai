import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "market_data.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


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