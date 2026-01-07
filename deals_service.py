from duckduckgo_search import DDGS
from datetime import datetime, timedelta
import pandas as pd
import database

class DealFinder:
    def __init__(self):
        self.chains = ["麥當勞", "肯德基", "星巴克", "必勝客", "漢堡王", "sukiya"]
        
    def fetch_latest_deals(self, force_refresh=False):
        """
        Fetch deals from cache or web.
        force_refresh: If True, ignore cache and re-fetch.
        """
        # 1. Check Cache
        if not force_refresh:
            cached_df = database.get_cached_deals()
            if not cached_df.empty:
                # Check date of first record
                last_fetched = cached_df.iloc[0]['fetched_date']
                last_date = datetime.strptime(last_fetched, "%Y-%m-%d")
                if datetime.now() - last_date < timedelta(days=7):
                    return cached_df, last_fetched

        # 2. Fetch from Web
        new_deals = []
        current_month = datetime.now().month
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        print("Fetching new deals from DuckDuckGo...")
        
        try:
            with DDGS() as ddgs:
                for chain in self.chains:
                    query = f"{chain} 優惠 {current_month}月"
                    try:
                        # Fetch top 2 results
                        results = list(ddgs.text(query, max_results=2))
                        
                        if results:
                            for res in results:
                                new_deals.append({
                                    "chain_name": chain,
                                    "title": res['title'],
                                    "link": res['href'],
                                    "source": "DuckDuckGo Search",
                                    "fetched_date": today_str
                                })
                        else:
                            raise Exception("No results found")

                    except Exception as e:
                        print(f"Error fetching {chain}: {e}")
                        # Fallback: Add a generic Google Search link
                        new_deals.append({
                            "chain_name": chain,
                            "title": f"{chain} 最新優惠 (點擊搜尋)",
                            "link": f"https://www.google.com/search?q={chain}+優惠",
                            "source": "Fallback",
                            "fetched_date": today_str
                        })
        except Exception as e:
            print(f"Critical DDGS Error: {e}")
            # Fallback for all chains if DDGS fails completely
            for chain in self.chains:
                # Avoid duplicates if some were already added
                if not any(d['chain_name'] == chain for d in new_deals):
                    new_deals.append({
                        "chain_name": chain,
                        "title": f"{chain} 最新優惠 (點擊搜尋)",
                        "link": f"https://www.google.com/search?q={chain}+優惠",
                        "source": "Fallback (Critical Error)",
                        "fetched_date": today_str
                    })

        # 3. Update Database
        if new_deals:
            database.update_deals(new_deals)
            return pd.DataFrame(new_deals), today_str
        else:
            return pd.DataFrame(), today_str
