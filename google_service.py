import requests

def get_ip_location():
    """
    Get current location based on IP address using ip-api.com.
    Returns a dict with 'lat' and 'lon' (or None on failure).
    """
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'success':
            return {'lat': data['lat'], 'lng': data['lon']} # Normalize to lat/lng
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
                "rating": place.get("rating", "N/A")
            })
        return places
    except Exception as e:
        print(f"Error searching places: {e}")
        return []
