from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_location_details(lat: float, lon: float) -> dict:
    geolocator = Nominatim(user_agent="urban_solar_engine_pro_v1")
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True, language='en', timeout=10)
    except (GeocoderTimedOut, GeocoderUnavailable):
        return {"city": "", "state": "Unknown"}
        
    if not location:
        return {"city": "", "state": "Unknown"}
        
    address = location.raw.get('address', {})
    state = address.get('state') or address.get('territory') or address.get('state_district') or "Unknown"
    city = address.get('city') or address.get('town') or address.get('village') or address.get('county') or ""
    
    return {"city": city, "state": state}