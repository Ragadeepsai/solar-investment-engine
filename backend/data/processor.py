import duckdb
import pandas as pd
from backend.models.solar_calculator import calculate_subsidy

def run_solar_engine(nasa_df: pd.DataFrame, state: str, panel_area: float, panel_type: str, ev_owner: bool):
    # 1. DUCKDB SQL: Dynamically query the CSV file for the exact state tariff
    tariff_query = f"""
        SELECT import_rate_inr 
        FROM read_csv_auto('data/state_tariff.csv') 
        WHERE LOWER(TRIM(state)) = LOWER(TRIM('{state}'))
    """
    try:
        tariff_df = duckdb.query(tariff_query).to_df()
        tariff = tariff_df['import_rate_inr'][0] if not tariff_df.empty else 6.5
    except Exception:
        tariff = 6.5 # National average fallback
        
    # 2. Panel specs (Calibrated to Power BI model)
    panel_specs = {
        'Budget': [0.20, 10500], 
        'Standard': [0.22, 12500], 
        'Premium': [0.24, 14500]
    }
    efficiency, cost_per_sqm = panel_specs[panel_type]
    
    # 3. DUCKDB SQL: Aggregate the NASA weather data
    weather_query = """
        SELECT 
            AVG(irradiance) as avg_daily_irradiance,
            (AVG(irradiance) * 365) as annual_irradiance
        FROM nasa_df
    """
    metrics = duckdb.query(weather_query).to_df()
    annual_irradiance = metrics['annual_irradiance'][0]
    
    # 4. Financial Math
    system_size_kw = (panel_area * efficiency * 1000) / 1000
    gross_cost = panel_area * cost_per_sqm
    subsidy = calculate_subsidy(system_size_kw)
    out_of_pocket = gross_cost - subsidy
    
    annual_generation_kwh = annual_irradiance * panel_area * efficiency * 0.75
    annual_savings = (annual_generation_kwh * tariff)
    if ev_owner:
        annual_savings += 20000 
        
    payback_years = out_of_pocket / annual_savings if annual_savings > 0 else 0
    
    return {
        "System Size (kW)": round(system_size_kw, 2),
        "Gross Cost (INR)": round(gross_cost, 2),
        "Subsidy (INR)": round(subsidy, 2),
        "Out of Pocket (INR)": round(out_of_pocket, 2),
        "Annual Savings (INR)": round(annual_savings, 2),
        "Payback Period (Years)": round(payback_years, 2)
    }
