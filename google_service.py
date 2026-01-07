import requests
from bs4 import BeautifulSoup

def get_ip_location():
    """
    Get current location based on IP address using ip-api.com.
    Returns a dict with 'lat' and 'lon' (or None on failure).
    """
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'success':
            return {'lat': data['lat'], 'lng': data['lon'], 'city': data.get('city', 'Unknown City')} # Normalize to lat/lng and include city
        else:
            return None
    except:
        return None

def search_nearby_places(keyword, location, api_key):
    """
    Search for places using Google Places API (Nearby Search).
    
    Args:
        keyword (str): Search term (e.g., "Fried Rice").
        location (str): "lat,lng" string.
        api_key (str): Google Maps API Key.
        
    Returns:
        list: A list of dictionaries containing place details (name, address, lat, lng).
    """
    endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": 1500, # 1.5 km radius
        "keyword": keyword,
        "key": api_key,
        "language": "zh-TW"
    }
    
    try:
        response = requests.get(endpoint, params=params)
        results = response.json().get('results', [])
        
        places = []
        for place in results:
            places.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"],
                "rating": place.get("rating", "N/A"),
                "user_ratings_total": place.get("user_ratings_total", 0),
                "place_id": place.get("place_id"),
                "website": place.get("website") # Note: nearbysearch often omits this, but we extract it if present
            })
        return places
    except Exception as e:
        print(f"Error searching places: {e}")
        return []

def get_website_preview(url):
    """
    Scrape the <title> and <meta name="description"> from the URL.
    Returns a summary string.
    """
    try:
        response = requests.get(url, timeout=3)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string.strip() if soup.title else "無標題"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc = meta_desc['content'].strip() if meta_desc and meta_desc.get('content') else "無描述"
        
        return f"標題: {title}\n描述: {desc}"
    except Exception:
        return "無法預覽官網內容"
