import sqlite3
import pandas as pd
import streamlit as st
import random
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import urllib.parse
import streamlit.components.v1 as components  # 用來嵌入地圖
import requests  # 新增：用來抓取 IP 位置

# --- 設定頁面配置 ---
st.set_page_config(page_title="今天吃什麼 (Dining Decision)", page_icon="🍱", layout="centered")

# --- ⚠️ 你的 Google Maps API Key ---
GOOGLE_MAPS_API_KEY = "AIzaSyBa6bjJALq6vPrTRVy7HuChBw1PcSCRX_w"

# --- 資料庫函式 ---
DB_FILE = "dining_v2.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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

def seed_data():
    """插入高雄三民區真實美食資料"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT count(*) FROM dining_records')
    if c.fetchone()[0] == 0:
        # 高雄三民區真實美食名單 (已篩選網路高評價)
        food_spots = [
            ("鴨肉飯", "三塊厝鴨肉飯"),
            ("意麵", "阿萬意麵"),
            ("生煎湯包", "上海生煎湯包"),
            ("肉圓", "三塊厝肉圓嫂"),
            ("麵線羹", "三民街老麵攤"),
            ("雞蛋酥", "方家雞蛋酥"),
            ("水冰/湯圓", "鹿仔草冰店"),
            ("包子", "舞一包子饅頭"),
            ("台菜", "老新台菜"),
            ("香腸", "新大港大腸香腸")
        ]
        
        data = []
        for _ in range(50): # 生成 50 筆模擬紀錄
            date = datetime.now().strftime("%Y-%m-%d")
            mood = random.choice([1, 2, 3])
            weather = random.choice([1, 2, 3])
            is_work = random.choice([0, 1])
            meal_type = random.choice(["早餐", "午餐", "晚餐"])
            food, restaurant = random.choice(food_spots)
            data.append((date, mood, weather, is_work, meal_type, food, restaurant))
        
        c.executemany('INSERT INTO dining_records (date, mood, weather, is_work, meal_type, food_name, restaurant_name) VALUES (?, ?, ?, ?, ?, ?, ?)', data)
        conn.commit()
        print("已插入高雄三民區真實資料。")
    conn.close()

def save_record(mood, weather, is_work, meal_type, food_name, restaurant_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute('INSERT INTO dining_records (date, mood, weather, is_work, meal_type, food_name, restaurant_name) VALUES (?, ?, ?, ?, ?, ?, ?)', 
              (date, mood, weather, is_work, meal_type, food_name, restaurant_name))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM dining_records", conn)
    conn.close()
    return df

# --- IP 定位函式 (新增) ---
def get_ip_location():
    try:
        # 使用免費的 ip-api.com 服務
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'success':
            return data
        else:
            return None
    except:
        return None

# --- 初始化 ---
init_db()
seed_data()

# --- 主程式 ---
st.title("🍱 今天吃什麼？ (高雄三民版)")
st.caption("AI 推薦 + Google Maps + IP 定位技術展示 🚀")

# 中文分頁
tab1, tab2, tab3 = st.tabs(["🍽️ 記錄餐點", "🤖 AI 推薦 & 定位", "📊 歷史數據"])

mood_map = {1: "開心 😊", 2: "普通 😐", 3: "鬱悶 😞"}
weather_map = {1: "晴天 ☀️", 2: "雨天 🌧️", 3: "陰天 ☁️"}

# --- Tab 1: 用餐紀錄 ---
with tab1:
    st.header("📝 記錄你的三民區美食地圖")
    col1, col2 = st.columns(2)
    with col1:
        mood = st.selectbox("心情", options=list(mood_map.keys()), format_func=lambda x: mood_map[x])
        weather = st.selectbox("天氣", options=list(weather_map.keys()), format_func=lambda x: weather_map[x])
    with col2:
        meal_types = ["早餐", "午餐", "晚餐", "宵夜"]
        meal_type = st.selectbox("餐別", meal_types)
        is_work_bool = st.checkbox("今天是工作日嗎？", value=True)
        is_work = 1 if is_work_bool else 0

    col3, col4 = st.columns(2)
    with col3:
        food_name = st.text_input("食物名稱", placeholder="例如：鴨肉飯")
    with col4:
        restaurant_name = st.text_input("餐廳/店家名稱", placeholder="例如：三塊厝鴨肉飯")
    
    if st.button("💾 儲存紀錄", type="primary"):
        if food_name and restaurant_name:
            save_record(mood, weather, is_work, meal_type, food_name, restaurant_name)
            st.success(f"已儲存：**{restaurant_name}** 的 {food_name}！")
        else:
            st.warning("請填寫完整的食物與餐廳名稱。")

# --- Tab 2: AI 推薦 (含 IP 定位) ---
with tab2:
    st.header("🔮 AI 幫你決定去哪吃")
    
    # --- 新增：IP 定位區塊 ---
    with st.expander("📍 檢視我的 IP 目前位置", expanded=False):
        if st.button("🔍 偵測我的位置"):
            with st.spinner("正在連線衛星與基地台..."):
                loc_data = get_ip_location()
                if loc_data:
                    st.success(f"定位成功！你的 IP: {loc_data['query']}")
                    st.write(f"🌍 城市: **{loc_data['city']}, {loc_data['regionName']}**")
                    st.write(f"🌐 經緯度: {loc_data['lat']}, {loc_data['lon']}")
                    
                    # 顯示位置地圖
                    map_url = f"https://www.google.com/maps/embed/v1/search?key={GOOGLE_MAPS_API_KEY}&center={loc_data['lat']},{loc_data['lon']}&zoom=14"
                    components.iframe(map_url, height=300)
                else:
                    st.error("無法抓取位置，請檢查網路連線。")

    st.markdown("---")
    st.subheader("🤖 輸入現在狀態")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        curr_mood = st.selectbox("目前心情", options=list(mood_map.keys()), format_func=lambda x: mood_map[x], key="p_m")
    with col_p2:
        curr_weather = st.selectbox("目前天氣", options=list(weather_map.keys()), format_func=lambda x: weather_map[x], key="p_w")
    with col_p3:
        curr_work_bool = st.checkbox("是否工作日", value=True, key="p_wk")
        curr_work = 1 if curr_work_bool else 0
    
    if st.button("🤖 幫我找三民區美食"):
        df = load_data()
        if len(df) < 5:
            st.warning("資料不足，請先到「記錄餐點」頁面輸入更多資料！")
        else:
            # AI 預測
            X = df[['mood', 'weather', 'is_work']]
            y = df['restaurant_name']
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X, y)
            
            input_data = pd.DataFrame([[curr_mood, curr_weather, curr_work]], columns=['mood', 'weather', 'is_work'])
            prediction_store = clf.predict(input_data)[0]
            
            st.markdown(f"### 📍 AI 強力推薦： **{prediction_store}**")
            
            # --- Google Maps Embed API ---
            # 將店家名稱編碼 + 強制加入「高雄三民區」以提高準確度
            search_query = urllib.parse.quote(f"高雄三民區 {prediction_store}")
            
            # 組合嵌入式地圖 URL
            embed_url = f"https://www.google.com/maps/embed/v1/search?key={GOOGLE_MAPS_API_KEY}&q={search_query}&zoom=16"
            
            st.markdown("👇 店家位置預覽：")
            components.iframe(embed_url, height=400)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.link_button(f"🚀 Google 導航 ({prediction_store})", f"https://www.google.com/maps/search/?api=1&query={search_query}")
            with col_b2:
                # 這裡可以做一個按鈕是「從我的位置出發」(使用 IP 經緯度)
                # 簡單版直接跳轉 Google Maps 路線規劃
                st.link_button("🚗 規劃路線", f"https://www.google.com/maps/dir/?api=1&destination={search_query}")

# --- Tab 3: 歷史紀錄 ---
with tab3:
    st.header("📊 三民區美食大數據")
    df = load_data()
    
    df_display = df.rename(columns={
        "date": "日期", "mood": "心情指數", "weather": "天氣指數", 
        "is_work": "工作日", "meal_type": "餐別", 
        "food_name": "食物", "restaurant_name": "餐廳"
    })
    
    st.dataframe(df_display, use_container_width=True)
    
    if not df.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("🏆 人氣餐廳排行榜")
            st.bar_chart(df['restaurant_name'].value_counts().head(5))
        with col_c2:
            st.subheader("🏆 熱門食物")
            st.bar_chart(df['food_name'].value_counts().head(5))