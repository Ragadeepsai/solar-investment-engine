from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_state(lat: float, lon: float) -> str:
    # Changed user agent to be more unique to avoid rate-limiting blocks
    geolocator = Nominatim(user_agent="urban_solar_engine_pro_v1")
    
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True, language='en', timeout=10)
    except (GeocoderTimedOut, GeocoderUnavailable):
        # If the API times out or blocks the IP, don't crash. 
        return "Unknown"
        
    if not location:
        return "Unknown"
        
    address = location.raw.get('address', {})
    
    # Check multiple keys to handle Union Territories and map quirks
    state = address.get('state') or address.get('territory') or address.get('state_district')
    
    if not state:
        return "Unknown"
        
    return state