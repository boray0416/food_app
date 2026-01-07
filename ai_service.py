import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import urllib.parse
import requests

class FoodRecommender:
    def __init__(self, google_maps_api_key):
        self.api_key = google_maps_api_key
        self.model = None

    def train_model(self, df):
        """Train the Random Forest model using the provided DataFrame."""
        if len(df) < 5:
            return False
        
        X = df[['mood', 'weather', 'is_work']]
        y = df['restaurant_name']
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        return True

    def predict(self, mood, weather, is_work):
        """Predict restaurant based on inputs."""
        if not self.model:
            return None
        
        input_data = pd.DataFrame([[mood, weather, is_work]], columns=['mood', 'weather', 'is_work'])
        prediction = self.model.predict(input_data)[0]
        return prediction

    def get_ip_location(self):
        """Get location data from ip-api.com."""
        try:
            response = requests.get('http://ip-api.com/json/')
            data = response.json()
            if data['status'] == 'success':
                return data
            else:
                return None
        except:
            return None

    def get_google_maps_url(self, query):
        """Generate Google Maps Embed URL."""
        search_query = urllib.parse.quote(query)
        embed_url = f"https://www.google.com/maps/embed/v1/search?key={self.api_key}&q={search_query}&zoom=16"
        return embed_url
