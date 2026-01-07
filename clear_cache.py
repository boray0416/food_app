import sqlite3

conn = sqlite3.connect("dining_system.db")
c = conn.cursor()
c.execute("DELETE FROM deals_cache")
conn.commit()
print("Cache cleared.")
conn.close()
