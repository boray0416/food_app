import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = "dining_v2.db"

# True NKUST Jiangong Campus Favorites
WEEKDAY_CHEAP_EATS = [
    ("學員小廚", "雞腿飯便當"),
    ("吉利自助餐", "排骨飯"),
    ("弘記炒飯", "肉絲蛋炒飯"),
    ("P剛打拋豬肉飯", "泰式打拋豬肉飯"),
    ("森碳柴燒餐盒", "烤雞腿飯"),
    ("御蕎園排骨飯", "炸排骨飯"),
    ("虎爺雞飯", "海南雞飯"),
    ("原香牛肉拉麵", "牛肉麵"),
    ("丹丹漢堡", "9號餐(麵線羹+漢堡)"),
    ("麵子粉大", "麻醬麵")
]

WEEKEND_BIG_MEALS = [
    ("鼎天味洪師傅薑母鴨", "薑母鴨套餐"),
    ("五鮮級平價鍋物", "龍骨湯底豬肉鍋"),
    ("牛魔王牛排", "厚切沙朗牛排"),
    ("開麻開辣", "麻辣鴛鴦鍋吃到飽"),
    ("藝鍋物", "牛奶起司鍋"),
    ("愛麻嗜麻辣美學", "招牌麻辣燙"),
    ("優異義義大利麵", "青醬蛤蜊義大利麵"),
    ("老潮派鑄鐵鍋燒", "叻沙鍋燒意麵"),
    ("江豪記臭豆腐", "脆皮臭豆腐+清蒸臭豆腐"),
    ("圓也日式創作料理", "鮭魚親子丼")
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ensure table exists (schema matches main.py)
    c.execute('''
        CREATE TABLE IF NOT EXISTS dining_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            mood INTEGER,
            weather INTEGER,
            is_work INTEGER,
            meal_type TEXT,
            food_name TEXT,
            restaurant_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def generate_data():
    print("Initializing database...")
    init_db()
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Generate data for the past 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    records = []
    
    print(f"Generating data from {start_date.date()} to {end_date.date()}...")
    
    current_date = start_date
    while current_date <= end_date:
        # Determine if it's a weekend (5=Saturday, 6=Sunday)
        is_weekend = current_date.weekday() >= 5
        is_work = 0 if is_weekend else 1
        
        # Determine number of meals today (1 or 2, occasional skip handled by logic or just simple 1-2 range)
        num_meals = random.randint(1, 2)
        
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Mood and Weather simulation
        # Weekends are generally happier (1=Happy, 2=Normal, 3=Sad)
        mood = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1] if is_weekend else [0.2, 0.5, 0.3])[0]
        weather = random.randint(1, 3) # 1=Sun, 2=Rain, 3=Cloud
        
        meal_types_pool = ["午餐", "晚餐"]
        
        for _ in range(num_meals):
            meal_type = table_meal = random.choice(meal_types_pool)
            if meal_type in meal_types_pool:
                meal_types_pool.remove(meal_type) # Avoid duplicate meal types for the same day
            
            # Select restaurant based on Logic
            if is_weekend:
                 # 30% chance to still eat cheap on weekends, 70% treat
                if random.random() < 0.7:
                    restaurant, food = random.choice(WEEKEND_BIG_MEALS)
                else:
                    restaurant, food = random.choice(WEEKDAY_CHEAP_EATS)
            else:
                # 90% chance cheap on weekdays, 10% treat
                if random.random() < 0.9:
                    restaurant, food = random.choice(WEEKDAY_CHEAP_EATS)
                else:
                    restaurant, food = random.choice(WEEKEND_BIG_MEALS)
            
            records.append((date_str, mood, weather, is_work, meal_type, food, restaurant))
            
        current_date += timedelta(days=1)
        
    print(f"Generated {len(records)} records.")
    
    # Batch Insert
    c.executemany('''
        INSERT INTO dining_records (date, mood, weather, is_work, meal_type, food_name, restaurant_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', records)
    
    conn.commit()
    conn.close()
    print("Data inserted successfully!")

if __name__ == "__main__":
    generate_data()
