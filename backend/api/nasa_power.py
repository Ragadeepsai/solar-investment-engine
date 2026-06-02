import requests
import pandas as pd
from datetime import datetime

MONTH_NAMES = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN', 
               7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
BASE_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"

def fetch_irradiance(lat: float, lon: float, start_year: int = 2002) -> pd.DataFrame:
    end_year = datetime.now().year - 1 
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": start_year,
        "end": end_year,
        "format": "JSON"
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    
    irradiance_dict = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
    fill_value = data['header']['fill_value']
    
    records = []
    for key, value in irradiance_dict.items():
        year, month = int(key[:4]), int(key[4:])
        if month == 13 or value == fill_value: 
            continue
        records.append({
            'year': year,
            'month_num': month,
            'month_name': MONTH_NAMES[month],
            'irradiance': value
        })
    df = pd.DataFrame(records).sort_values(['year', 'month_num']).reset_index(drop=True)
    return df
