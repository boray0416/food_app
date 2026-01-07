import streamlit as st
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# Import custom modules
import database
import google_service

# --- Configuration ---
st.set_page_config(page_title="Dining Decision System", page_icon="🍱", layout="centered")
GOOGLE_MAPS_API_KEY = "AIzaSyBa6bjJALq6vPrTRVy7HuChBw1PcSCRX_w"

# --- Initialize Database ---
database.init_db()

# --- UI Maps ---
mood_map = {1: "開心 😊", 2: "普通 😐", 3: "鬱悶 😞"}
weather_map = {1: "晴天 ☀️", 2: "雨天 🌧️", 3: "陰天 ☁️"}
time_slot_map = {"早餐": "早餐 🍳", "午餐": "午餐 🍱", "晚餐": "晚餐 🍽️", "宵夜": "宵夜 🍢"}

# --- Main App ---
st.title("🍱 今天吃什麼？ (定位版)")

tab1, tab2, tab3 = st.tabs(["🍽️ 記錄餐點", "🤖 AI 推薦", "📊 歷史數據"])

# --- Tab 1: Record Meal ---
with tab1:
    st.header("📍 記錄你的美食足跡")
    
    # Step 1: Environment
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("日期", datetime.now())
        time_slot = st.selectbox("時段", list(time_slot_map.keys()), format_func=lambda x: time_slot_map[x])
        is_work = st.checkbox("今天是工作日？", value=True)
    with col2:
        mood = st.selectbox("心情", list(mood_map.keys()), format_func=lambda x: mood_map[x])
        weather = st.selectbox("天氣", list(weather_map.keys()), format_func=lambda x: weather_map[x])
    
    st.markdown("---")
    
    # Step 2: Location
    st.subheader("1. 取得位置")
    if 'current_location' not in st.session_state:
        st.session_state.current_location = None

    if st.button("📍 取得我的位置 (IP)"):
        with st.spinner("正在定位..."):
            loc = google_service.get_ip_location()
            if loc:
                st.session_state.current_location = loc
                st.success(f"已定位：{loc['lat']}, {loc['lng']}")
            else:
                st.error("無法取得位置")

    # Step 3: Search
    st.subheader("2. 搜尋附近餐廳")
    search_keyword = st.text_input("你想吃什麼？", placeholder="例如：炒飯、拉麵...")
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []

    if st.button("🔍 搜尋附近餐廳"):
        if not st.session_state.current_location:
            st.warning("請先取得位置！")
        elif not search_keyword:
            st.warning("請輸入想吃的食物！")
        else:
            with st.spinner("搜尋 Google Maps 中..."):
                loc_str = f"{st.session_state.current_location['lat']},{st.session_state.current_location['lng']}"
                results = google_service.search_nearby_places(search_keyword, loc_str, GOOGLE_MAPS_API_KEY)
                st.session_state.search_results = results
                if not results:
                    st.info("附近找不到相關餐廳。")
    
    # Step 4: Selection
    selected_place = None
    if st.session_state.search_results:
        st.subheader("3. 選擇餐廳")
        
        # Create options list for display
        options = [f"{p['name']} ({p['address']})" for p in st.session_state.search_results]
        selection = st.radio("搜尋結果：", options)
        
        # Find the selected place object
        index = options.index(selection)
        selected_place = st.session_state.search_results[index]
        
        # Show map of selected place
        st.map(pd.DataFrame({'lat': [selected_place['lat']], 'lon': [selected_place['lng']]}))
        
        st.info(f"已選擇：**{selected_place['name']}**")

    # Step 5: Save
    st.markdown("---")
    if st.button("💾 儲存紀錄", type="primary"):
        if selected_place:
            database.save_record(
                date.strftime("%Y-%m-%d"), 
                time_slot, 
                mood, 
                weather, 
                1 if is_work else 0, 
                search_keyword, # Use the search keyword as the food name
                selected_place['name'], 
                selected_place['lat'], 
                selected_place['lng']
            )
            st.success(f"已儲存：**{selected_place['name']}** (食物：{search_keyword})")
        else:
            st.warning("請先搜尋並選擇一家餐廳！")

# --- Tab 2: AI Prediction ---
with tab2:
    st.header("🔮 AI 幫你決定")
    
    df = database.load_history()
    
    if len(df) < 5:
        st.warning(f"⚠️ 資料不足！目前只有 {len(df)} 筆紀錄。請先記錄至少 5 筆餐點才能啟用 AI 推薦。")
    else:
        st.subheader("輸入目前狀態")
        c1, c2, c3 = st.columns(3)
        p_mood = c1.selectbox("目前心情", list(mood_map.keys()), format_func=lambda x: mood_map[x], key="p_m")
        p_weather = c2.selectbox("目前天氣", list(weather_map.keys()), format_func=lambda x: weather_map[x], key="p_w")
        p_work = c3.checkbox("工作日？", value=True, key="p_wk")
        
        if st.button("🤖 AI 推薦"):
            # Train Model
            X = df[['mood', 'weather', 'is_work']]
            y = df['restaurant_name']
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X, y)
            
            # Predict
            input_data = pd.DataFrame([[p_mood, p_weather, 1 if p_work else 0]], columns=['mood', 'weather', 'is_work'])
            prediction = clf.predict(input_data)[0]
            
            st.success(f"AI 推薦你去吃： **{prediction}**")
            
            # Find details if available in history
            record = df[df['restaurant_name'] == prediction].iloc[0]
            if not pd.isna(record['lat']):
                st.map(pd.DataFrame({'lat': [record['lat']], 'lon': [record['lng']]}))

# --- Tab 3: History ---
with tab3:
    st.header("📊 歷史紀錄")
    df = database.load_history()
    st.dataframe(df, use_container_width=True)
