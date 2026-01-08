import streamlit as st
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# Import custom modules
import database
import google_service
import urllib.parse
from streamlit_js_eval import get_geolocation
import streamlit.components.v1 as components  # For Map Embedding
import requests # For IP Location

# --- Configuration ---
st.set_page_config(page_title="今天吃什麼", page_icon="🍱", layout="centered")

# 嘗試從 Secrets 讀取 API Key，失敗則使用 Hardcoded Key (演示用)
try:
    GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
except:
    GOOGLE_MAPS_API_KEY = "AIzaSyBa6bjJALq6vPrTRVy7HuChBw1PcSCRX_w"

# --- iOS Style CSS (Dark Mode) ---
st.markdown("""
    <style>
        /* Global Font & Colors */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #f2f2f7; /* Light Gray Text */
            background-color: #1c1c1e; /* Dark Background */
        }
        
        /* App Background */
        .stApp {
            background-color: #000000; /* Deep Black Background */
        }

        /* Buttons (iOS Blue Style) */
        .stButton > button {
            background-color: #0a84ff; /* iOS Dark Mode Blue */
            color: white;
            border-radius: 12px;
            border: none;
            padding: 10px 20px;
            font-weight: 500;
            width: 100%;
            transition: opacity 0.2s;
        }
        .stButton > button:hover {
            opacity: 0.8;
            color: white;
            border: none;
        }
        .stButton > button:active {
            opacity: 0.6;
        }

        /* Inputs (Dark Gray) */
        .stTextInput > div > div, .stSelectbox > div > div, .stDateInput > div > div {
            background-color: #1c1c1e;
            color: white;
            border-radius: 10px;
            border: 1px solid #3a3a3c;
        }
        .stTextInput input, .stSelectbox div[data-baseweb="select"] div {
            color: white;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            background-color: #1c1c1e;
            padding: 10px 20px;
            border-radius: 16px;
            border: 1px solid #2c2c2e;
        }
        .stTabs [data-baseweb="tab"] {
            height: auto;
            white-space: pre-wrap;
            border-radius: 8px;
            padding-top: 8px;
            padding-bottom: 8px;
            color: #8e8e93; /* Gray for unselected */
        }
        .stTabs [aria-selected="true"] {
            background-color: #2c2c2e;
            color: #0a84ff;
            font-weight: 600;
        }
        
        /* Expander / Cards */
        .streamlit-expanderHeader {
            background-color: #1c1c1e;
            color: #f2f2f7;
            border-radius: 12px;
            margin-bottom: 8px;
            border: 1px solid #2c2c2e;
        }
        .streamlit-expanderContent {
            background-color: #1c1c1e;
            color: #f2f2f7;
            border-radius: 12px;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 700;
            color: #f2f2f7;
        }
        
        /* Remove default streamlit menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
    </style>
""", unsafe_allow_html=True)

# --- Initialize Database ---
database.init_db()

# --- Helper Functions ---
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

# --- UI Maps ---
mood_map = {1: "開心", 2: "普通", 3: "鬱悶"}
weather_map = {1: "晴天", 2: "雨天", 3: "陰天"}
time_slot_map = {"早餐": "早餐", "午餐": "午餐", "晚餐": "晚餐", "宵夜": "宵夜"}

# --- Main App ---
st.title("今天吃什麼")

tab1, tab2, tab3, tab4 = st.tabs(["探索", "推薦", "紀錄", "優惠"])

# --- Tab 1: Record Meal ---
with tab1:
    st.subheader("探索美食足跡")
    
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
    
    # 全方位定位系統
    loc_col1, loc_col2 = st.columns(2)
    
    with loc_col1:
        # A. 瀏覽器精準定位 (GPS)
        # st.markdown("###### 📍 GPS 精準定位") # User requested to hide this
        browser_loc = get_geolocation(component_key='get_geolocation')
        if browser_loc:
            st.session_state.current_location = {
                'lat': browser_loc['coords']['latitude'],
                'lng': browser_loc['coords']['longitude']
            }
    
    with loc_col2:
        # B. 演示模式 (強制高科建工)
        st.markdown("###### 🏫 快速設定")
        if st.button("設為高科建工"):
            st.session_state.current_location = {'lat': 22.6515122, 'lng': 120.3286609}
            st.toast("已切換至高科大建工校區", icon="🚀")

    # 顯示目前位置資訊與地圖
    if st.session_state.current_location:
        lat = st.session_state.current_location['lat']
        lng = st.session_state.current_location['lng']
        st.info(f"目前位置：{lat:.4f}, {lng:.4f}")
        
        # 顯示小地圖確認
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lng]}), zoom=14)

    # Step 3: Search
    st.subheader("2. 搜尋附近餐廳")
    search_keyword = st.text_input("你想吃什麼？", placeholder="例如：炒飯、拉麵...")
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []

    if st.button("搜尋附近餐廳"):
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
        options = []
        for p in st.session_state.search_results:
            rating_str = f"⭐ {p.get('rating', 'N/A')}"
            reviews = f"({p.get('user_ratings_total', 0)}則評論)"
            options.append(f"{p['name']} - {rating_str} {reviews}")
            
        selection = st.radio("搜尋結果：", options)
        
        # Find the selected place object
        index = options.index(selection)
        selected_place = st.session_state.search_results[index]
        
        # Show map of selected place
        st.map(pd.DataFrame({'lat': [selected_place['lat']], 'lon': [selected_place['lng']]}))
        
        # Display details and Menu Link
        st.info(f"已選擇：**{selected_place['name']}**")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            if selected_place.get('place_id'):
                place_id = selected_place['place_id']
                query_name = urllib.parse.quote(selected_place['name'])
                # Google Maps Deep Link
                menu_url = f"https://www.google.com/maps/search/?api=1&query={query_name}&query_place_id={place_id}"
                st.link_button("查看菜單/詳情 (使用 Google Maps)", menu_url)
        
        with col_m2:
            # Feature A: Google Image Search
            img_query = urllib.parse.quote(f"{selected_place['name']} 菜單")
            img_search_url = f"https://www.google.com/search?q={img_query}&tbm=isch"
            st.link_button("搜尋該店菜單 (Google 圖片)", img_search_url, help="點擊按鈕可直接查看網友上傳的菜單圖片")

        # Feature B: Official Website Preview
        if selected_place.get('website'):
            st.markdown("---")
            st.subheader("官網資訊摘要")
            with st.spinner("正在預覽官網內容..."):
                preview_text = google_service.get_website_preview(selected_place['website'])
                st.info(preview_text)
                st.link_button("前往官網", selected_place['website'])

    # Step 5: Save
    st.markdown("---")
    if st.button("儲存紀錄", type="primary"):
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
    st.subheader("AI 幫你決定")
    
    # --- UI Refactor: IP Location Block ---
    with st.container(border=True):
        st.write("📍 **目前位置偵測**")
        if st.button("📍 偵測我的位置", use_container_width=True):
            loc_data = None
            with st.status("正在連線衛星與基地台...", expanded=True) as status:
                st.write("🔍 正在搜尋 IP Address...")
                loc_data = get_ip_location()
                
                if loc_data:
                    status.update(label="定位完成！", state="complete", expanded=False)
                    # Update Session State immediately
                    st.session_state.current_location = {
                        'lat': loc_data['lat'],
                        'lng': loc_data['lon'],
                        'city': loc_data['city'],
                        'region': loc_data['regionName'],
                        'country': loc_data['country']
                    }
                else:
                    status.update(label="定位失敗", state="error")
                    st.error("無法抓取位置，請檢查網路連線。")
        
        # Display Location Data (Persistent)
        if st.session_state.get('current_location'):
            curr_loc = st.session_state.current_location
            # 使用 Columns 顯示數據 (Visual Metrics)
            m1, m2 = st.columns(2)
            with m1:
                st.metric(label="城市/地區", value=f"{curr_loc.get('city', 'Unknown')}")
            with m2:
                st.metric(label="經緯度", value=f"{curr_loc['lat']:.4f}, {curr_loc['lng']:.4f}")
            
            if 'region' in curr_loc:
                st.caption(f"完整位置：{curr_loc['region']}, {curr_loc.get('country','')}")
            
            # 顯示位置地圖
            # map_url = f"https://www.google.com/maps/embed/v1/search?key={GOOGLE_MAPS_API_KEY}&q={curr_loc['lat']},{curr_loc['lng']}&zoom=14"
            # components.iframe(map_url, height=250)
            
            # 使用 st.map 替代 embed api 以避免 key 問題
            st.map(pd.DataFrame({'lat': [curr_loc['lat']], 'lon': [curr_loc['lng']]}), zoom=14)

    st.markdown("---")
    
    df = database.load_history()
    
    if len(df) < 5:
        st.warning(f"⚠️ 資料不足！目前只有 {len(df)} 筆紀錄。請先記錄至少 5 筆餐點才能啟用 AI 推薦。")
    else:
        st.subheader("輸入目前狀態")
        c1, c2, c3 = st.columns(3)
        p_mood = c1.selectbox("目前心情", list(mood_map.keys()), format_func=lambda x: mood_map[x], key="p_m")
        p_weather = c2.selectbox("目前天氣", list(weather_map.keys()), format_func=lambda x: weather_map[x], key="p_w")
        p_work = c3.checkbox("工作日？", value=True, key="p_wk")
        
        if st.button("開始推薦"):
            # Train Model
            X = df[['mood', 'weather', 'is_work']]
            y = df['restaurant_name']
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X, y)
            
            # Predict Probabilities
            input_data = pd.DataFrame([[p_mood, p_weather, 1 if p_work else 0]], columns=['mood', 'weather', 'is_work'])
            probs = clf.predict_proba(input_data)[0]
            
            # Get top 3 recommendations
            top_indices = probs.argsort()[-3:][::-1]
            top_restaurants = [(clf.classes_[i], probs[i]) for i in top_indices]
            
            st.success(f"首選推薦： **{top_restaurants[0][0]}** ({top_restaurants[0][1]*100:.1f}%)")
            
            # Display Top 3
            st.write("其他候選：")
            for name, prob in top_restaurants[1:]:
                st.write(f"- **{name}** ({prob*100:.1f}%)")
            
            # Find details for the top prediction
            prediction = top_restaurants[0][0]
            record = df[df['restaurant_name'] == prediction].iloc[0]
            
            # --- Google Maps Embed API (Improved) ---
            search_query = urllib.parse.quote(f"高雄三民區 {prediction}")
            
            # 優先使用資料庫中的經緯度顯示 st.map
            if not pd.isna(record['lat']) and not pd.isna(record['lng']):
                st.write("店家位置預覽：")
                st.map(pd.DataFrame({'lat': [record['lat']], 'lon': [record['lng']]}), zoom=16)
            else:
                # 只有當沒有經緯度時才嘗試 Embed (或是顯示提示)
                st.warning("查無座標資訊，請使用下方按鈕開啟導航。")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.link_button(f"Google 導航 ({prediction})", f"https://www.google.com/maps/search/?api=1&query={search_query}")
            with col_b2:
                 st.link_button("規劃路線", f"https://www.google.com/maps/dir/?api=1&destination={search_query}")

# --- Tab 3: History ---
with tab3:
    st.subheader("美食大數據")
    df = database.load_history()
    
    # Rename columns for display
    df_display = df.rename(columns={
        "date": "日期", "mood": "心情指數", "weather": "天氣指數", 
        "is_work": "工作日", "meal_type": "餐別", 
        "food_name": "食物", "restaurant_name": "餐廳",
        "lat": "緯度", "lng": "經度"
    })
    
    st.dataframe(df_display, use_container_width=True)
    
    if not df.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("人氣排行榜")
            st.bar_chart(df['restaurant_name'].value_counts().head(5))
        with col_c2:
            st.subheader("熱門食物")
            st.bar_chart(df['food_name'].value_counts().head(5))

# --- Tab 4: Weekly Deals ---
with tab4:
    st.subheader("連鎖餐廳本週優惠")
    st.caption("自動搜尋各大連鎖餐廳的最新優惠資訊 (每週更新)")
    
    # Initialize DealFinder
    from deals_service import DealFinder
    finder = DealFinder()
    
    # Force Refresh Button
    col_d1, col_d2 = st.columns([3, 1])
    with col_d2:
        if st.button("刷新", type="secondary"):
            with st.spinner("正在重新搜尋優惠..."):
                deals_df, update_date = finder.fetch_latest_deals(force_refresh=True)
                st.success("已更新！")
                st.rerun()
    
    # Load Deals
    deals_df, update_date = finder.fetch_latest_deals()
    
    st.caption(f"資料更新日期: {update_date}")
    
    if not deals_df.empty:
        # Group by chain name
        chains = deals_df['chain_name'].unique()
        for chain in chains:
            with st.expander(f"{chain}", expanded=True):
                chain_deals = deals_df[deals_df['chain_name'] == chain]
                for _, row in chain_deals.iterrows():
                    st.markdown(f"**[{row['title']}]({row['link']})**")
                    st.caption(f"來源: {row['source']}")
    else:
        st.warning("目前無法取得優惠資訊，請稍後再試或點擊強制刷新。")
