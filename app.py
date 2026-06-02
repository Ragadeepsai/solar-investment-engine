import streamlit as st
from backend.api.nasa_power import fetch_irradiance
from backend.api.geocoding import get_state
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
            state = get_state(lat, lon)
            st.success(f"📍 Location identified: **{state}**")
            
            nasa_df = fetch_irradiance(lat, lon)
            results = run_solar_engine(nasa_df, state, panel_area, panel_type, ev_owner)
            
            # Display KPI Cards
            col1, col2, col3 = st.columns(3)
            col1.metric("Gross Upfront Cost", f"₹ {results['Gross Cost (INR)']:,}")
            col2.metric("PM Surya Ghar Subsidy", f"₹ {results['Subsidy (INR)']:,}")
            col3.metric("Out of Pocket Cost", f"₹ {results['Out of Pocket (INR)']:,}")
            
            col4, col5, col6 = st.columns(3)
            col4.metric("True Payback Period", f"{results['Payback Period (Years)']} Years")
            col5.metric("Total Annual Savings", f"₹ {results['Annual Savings (INR)']:,}")
            col6.metric("System Size", f"{results['System Size (kW)']} kW")
            
            st.info(f"💡 For a {panel_area} sqm roof in {state}, your {panel_type} system pays for itself in just {results['Payback Period (Years)']} years.")
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
