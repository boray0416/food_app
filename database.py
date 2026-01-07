import sqlite3
import pandas as pd

DB_FILE = "dining_system.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Dining Records Table (Single User)
    c.execute('''
        CREATE TABLE IF NOT EXISTS dining_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mood INTEGER,
            weather INTEGER,
            is_work INTEGER,
            meal_type TEXT,
            food_name TEXT,
            restaurant_name TEXT,
            lat REAL,
            lng REAL
        )
    ''')

    # 2. Deals Cache Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS deals_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_name TEXT,
            title TEXT,
            link TEXT,
            source TEXT,
            fetched_date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# --- Dining Records ---
def save_record(date, meal_type, mood, weather, is_work, food_name, restaurant_name, lat, lng):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO dining_records (date, meal_type, mood, weather, is_work, food_name, restaurant_name, lat, lng) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, meal_type, mood, weather, is_work, food_name, restaurant_name, lat, lng))
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM dining_records", conn)
    conn.close()
    return df

# --- Deals Cache ---
def get_cached_deals():
    """Retrieve deals from cache."""
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM deals_cache", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def update_deals(deals_list):
    """Clear cache and save new deals."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM deals_cache") # Clear old cache
    
    for deal in deals_list:
        c.execute('''
            INSERT INTO deals_cache (chain_name, title, link, source, fetched_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (deal['chain_name'], deal['title'], deal['link'], deal['source'], deal['fetched_date']))
            
    conn.commit()
    conn.close()

