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
    
    # Create deals_cache table
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

# --- Deals Cache Methods ---

def get_cached_deals():
    """Get all cached deals."""
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM deals_cache", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def update_deals(deals_list):
    """
    Update the cache with new deals.
    deals_list: list of dicts {'chain_name', 'title', 'link', 'source', 'fetched_date'}
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Clear old deals to avoid duplicates/outdated info (Simple strategy: wipe and replace)
    # Or we can just wipe everything since we re-fetch all chains at once
    c.execute("DELETE FROM deals_cache")
    
    c.executemany('''
        INSERT INTO deals_cache (chain_name, title, link, source, fetched_date)
        VALUES (:chain_name, :title, :link, :source, :fetched_date)
    ''', deals_list)
    
    conn.commit()
    conn.close()

def clear_old_deals():
    """Clear deals older than 7 days (Optional helper)."""
    # Since update_deals wipes the table, this might not be strictly necessary 
    # unless we want partial updates. For now, we rely on update_deals.
    pass
