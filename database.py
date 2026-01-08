import sqlite3
import pandas as pd

DB_FILE = "dining_v2.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Dining Records Table (Consolidated Schema from main.py)
    # Note: 'lat' and 'lng' were in dining_system.db but removed in dining_v2.db initial version
    # We should add them back if we want to support storing location
    # But for now let's match the schema in dining_v2.db which generate_data.py uses
    # dining_v2.db schema: id, date, mood, weather, is_work, meal_type, food_name, restaurant_name
    # AND ADD lat, lng to support app.py functionality
    
    # Check if table exists to decide migration or alter
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dining_records'")
    if not c.fetchone():
        c.execute('''
            CREATE TABLE dining_records (
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
    else:
        # Check if lat/lng columns exist, if not add them
        c.execute("PRAGMA table_info(dining_records)")
        columns = [row[1] for row in c.fetchall()]
        if 'lat' not in columns:
            c.execute("ALTER TABLE dining_records ADD COLUMN lat REAL")
        if 'lng' not in columns:
            c.execute("ALTER TABLE dining_records ADD COLUMN lng REAL")

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

