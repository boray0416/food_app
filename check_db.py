import sqlite3
import os

files = ["dining_system.db", "dining_v2.db"]

for db_file in files:
    if os.path.exists(db_file):
        print(f"--- Checking {db_file} ---")
        try:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            
            # Get tables
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()
            print(f"Tables: {[t[0] for t in tables]}")
            
            for t in tables:
                table_name = t[0]
                try:
                    c.execute(f"SELECT count(*) FROM {table_name}")
                    count = c.fetchone()[0]
                    print(f"  {table_name}: {count} rows")
                except:
                    print(f"  {table_name}: Error counting")
            conn.close()
        except Exception as e:
            print(f"Error reading {db_file}: {e}")
    else:
        print(f"{db_file} does not exist.")
