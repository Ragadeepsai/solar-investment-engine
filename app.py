import streamlit as st
import plotly.graph_objects as go
from backend.api.nasa_power import fetch_irradiance
from backend.api.geocoding import get_location_details
from backend.data.processor import run_solar_engine

st.set_page_config(page_title="Solar Decision Engine", layout="wide")
st.title("☀️ Urban India Solar Investment Decision Engine")
st.markdown("### Find out exactly when your solar panels will pay for themselves.")

st.sidebar.header("Location & Specs")
lat = st.sidebar.number_input("Latitude", value=12.9716, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=77.5946, format="%.4f")
panel_area = st.sidebar.slider("Roof Area (sqm)", 10, 100, 25)
panel_type = st.sidebar.selectbox("Panel Type", ["Budget", "Standard", "Premium"])
ev_owner = st.sidebar.checkbox("I own an EV (Adds ₹20,000/yr savings)", value=False)

if st.sidebar.button("Calculate ROI", type="primary"):
    with st.spinner("Connecting to NASA Satellites & Geocoding..."):
        try:
            loc_data = get_location_details(lat, lon)
            state = loc_data["state"]
            city = loc_data["city"]
            display_loc = f"{city}, {state}" if city else state
            
            st.success(f"📍 Location identified: **{display_loc}**")
            
            nasa_df = fetch_irradiance(lat, lon)
            results = run_solar_engine(nasa_df, state, panel_area, panel_type, ev_owner)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Gross Upfront Cost", f"₹ {results['Gross Cost (INR)']:,}")
            col2.metric("PM Surya Ghar Subsidy", f"₹ {results['Subsidy (INR)']:,}")
            col3.metric("Out of Pocket Cost", f"₹ {results['Out of Pocket (INR)']:,}")
            
            col4, col5, col6 = st.columns(3)
            col4.metric("True Payback Period", f"{results['Payback Period (Years)']} Years")
            col5.metric("Total Annual Savings", f"₹ {results['Annual Savings (INR)']:,}")
            col6.metric("System Size", f"{results['System Size (kW)']} kW")
            
            st.info(f"💡 For a {panel_area} sqm roof in {display_loc}, your {panel_type} system pays for itself in just {results['Payback Period (Years)']} years.")
            
            st.markdown("---")
            st.markdown("### 25-Year Cumulative Cash Flow")
            fig = go.Figure()
            years = list(range(26))
            cf = results['Cumulative Cash Flow']
            
            fig.add_trace(go.Scatter(
                x=years, y=cf,
                mode='lines+markers',
                name='Cumulative Cash Flow',
                line=dict(color='#2ecc71', width=2),
                fill='tozeroy',
                fillcolor='rgba(46, 204, 113, 0.1)'
            ))
            fig.add_hline(y=0, line_dash='dash', line_color='red', annotation_text='Break-even')
            fig.update_layout(
                xaxis_title='Year',
                yaxis_title='₹ Cash Flow',
                hovermode='x unified',
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
# --- ARCHITECTURE EXPANDER ---
            st.markdown("---")
            with st.expander("🛠️ How this engine works (Under the Hood)"):
                st.markdown("""
                ### The Data Engineering Pipeline
                This application is not a static calculator. It is a dynamic data product powered by a real-time analytics pipeline:
                
                * 🛰️ **Live Satellite Telemetry (NASA POWER API):** When you input coordinates, the backend pings NASA's REST API to fetch over 2 decades of historical solar irradiance data for your exact micro-location.
                * 📍 **Dynamic Geocoding (Nominatim):** Coordinates are reverse-geocoded to pinpoint your State, triggering a lookup against a custom database of 36 regional electricity tariffs.
                * 🦆 **In-Memory SQL Analytics (DuckDB):** The raw JSON data from NASA is converted into Pandas DataFrames and aggregated in milliseconds using DuckDB's lightning-fast in-memory SQL engine.
                * 🏛️ **Business Logic:** System sizing and out-of-pocket costs are dynamically calculated using the latest PM-Surya Ghar subsidy capacity tiers.
                
                *Architected and deployed by Sai Ragadeep using Python, DuckDB, and Streamlit.*
                """)