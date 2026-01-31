"""
Database Migration Script - Add Transaction Analytics Columns

Adds new columns to the existing database without losing data:
- tx_count, total_received_btc, total_sent_btc, wallet_balance
- first_tx_date, last_tx_date, wallet_age_days
- is_mixer_pattern, is_high_volume
"""

import sqlite3
import os

DB_PATH = 'crypto_investigation.db'

def migrate_database():
    """Add new transaction analytics columns to Address table"""
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[INFO] Starting database migration...")
    
    # List of new columns to add
    migrations = [
        ("tx_count", "INTEGER DEFAULT 0"),
        ("total_received_btc", "REAL DEFAULT 0.0"),
        ("total_sent_btc", "REAL DEFAULT 0.0"),
        ("wallet_balance", "REAL DEFAULT 0.0"),
        ("first_tx_date", "DATETIME"),
        ("last_tx_date", "DATETIME"),
        ("wallet_age_days", "INTEGER DEFAULT 0"),
        ("is_mixer_pattern", "BOOLEAN DEFAULT 0"),
        ("is_high_volume", "BOOLEAN DEFAULT 0"),
    ]
    
    for column_name, column_type in migrations:
        try:
            sql = f"ALTER TABLE addresses ADD COLUMN {column_name} {column_type}"
            cursor.execute(sql)
            print(f"[SUCCESS] Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"[SKIP] Column already exists: {column_name}")
            else:
                print(f"[ERROR] Failed to add {column_name}: {e}")
                return False
    
    conn.commit()
    conn.close()
    
    print("[SUCCESS] Database migration complete!")
    return True


if __name__ == "__main__":
    migrate_database()
