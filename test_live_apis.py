import sys
import os

# Add workspace root to sys.path to enable backend module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.api.geocoding import get_location_details
from backend.api.nasa_power import fetch_irradiance

def main():
    print("--- 1. Testing Live Geocoding API (Detailed) ---")
    try:
        loc_data = get_location_details(12.9716, 77.5946)
        print(f"Location dictionary: {loc_data}")
        print(f"City: {loc_data.get('city')}, State: {loc_data.get('state')}")
    except Exception as e:
        print(f"Geocoding API Call Failed: {e}")
        
    print("\n--- 2. Testing Live NASA POWER API ---")
    try:
        df = fetch_irradiance(12.9716, 77.5946)
        print(f"DataFrame Shape: {df.shape}")
        print("DataFrame Head:")
        print(df.head())
    except Exception as e:
        print(f"NASA POWER API Call Failed: {e}")

if __name__ == "__main__":
    main()
