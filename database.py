import sqlite3
import pandas as pd

DB_FILE = "dining_system.db"

def init_db():
    """Initialize the database with the dining_records table. No seed data."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS dining_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time_slot TEXT,
            mood INTEGER,
            weather INTEGER,
            is_work INTEGER,
            food_name TEXT,
            restaurant_name TEXT,
            lat REAL,
            lng REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_record(date, time_slot, mood, weather, is_work, food_name, restaurant_name, lat, lng):
    """Save a single dining record to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO dining_records 
        (date, time_slot, mood, weather, is_work, food_name, restaurant_name, lat, lng) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, time_slot, mood, weather, is_work, food_name, restaurant_name, lat, lng))
    conn.commit()
    conn.close()

def load_history():
    """Load all records from the database."""
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM dining_records", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df
