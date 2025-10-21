import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page configuration ---
st.set_page_config(page_title="Apollo 17 Lunar Regolith Data", initial_sidebar_state="collapsed")

st.title("Apollo 17 Lunar Regolith Data")

st.header("The Apollo 17 Mission")
st.write("""
The Soil Mechanics Investigation during the Apollo 17 mission was primarily passive, as no dedicated soil mechanics equipment was included.
The results were therefore derived mainly from analysis of rover track patterns, astronaut observations, and photographic documentation of surface interactions.

The internal friction angle of the lunar soil was estimated from the geometry of rover tracks and astronaut footprints, assuming a known value for the bulk density of the surface material.
These analyses provided qualitative confirmation of the soil’s mechanical properties as observed during previous missions.
""")

# --- Data and plot ---
st.header("Lunar Regolith Density Variation with Depth")

# Original data with depth ranges
data = pd.DataFrame({
    "Testing Method": [
        "Drive tube", "Drive tube", "Drive tube", "Drive tube",
        "Drive tube", "Drive tube", "Drive tube", "Drive tube",
        "Drill stem", "Drill stem", "Drill stem", "Drill stem", "Drill stem", "Drill stem"
    ],
    "Depth range (cm)": [
        "0-22", "22-70", "0-33", "33-71",
        "0-16", "0-20", "20-71", "0-28",
        "0-305", "0-305", "0-305", "0-305", "0-305", "0-305"
    ],
    "Density (g/cm³)": [1.6, 1.73, 2.04, 2.29, 1.57, 1.67, 1.74, 1.77, 1.99, 1.8, 1.85, 1.84, 1.83, 1.74],
    "Porosity (%)": ["NA"] * 14,
    "Force Applied (N)": ["NA"] * 14
})

# --- Convert depth ranges into numeric start/end points ---
expanded_data = []

for _, row in data.iterrows():
    try:
        start, end = map(float, row["Depth range (cm)"].split("-"))
        # Add two rows for start and end depth (same density)
        expanded_data.append({"Depth (cm)": start, "Density (g/cm³)": row["Density (g/cm³)"], "Testing Method": row["Testing Method"]})
        expanded_data.append({"Depth (cm)": end, "Density (g/cm³)": row["Density (g/cm³)"], "Testing Method": row["Testing Method"]})
    except Exception:
        pass

expanded_df = pd.DataFrame(expanded_data).sort_values(by="Depth (cm)")

# --- Plot ---
fig = px.line(
    expanded_df,
    x="Depth (cm)",
    y="Density (g/cm³)",
    color="Testing Method",
    title="Lunar Regolith Density Profile with Depth",
    markers=True
)
fig.update_yaxes(autorange="reversed")  # Optional: makes it look like increasing depth goes downward
st.plotly_chart(fig, use_container_width=True)

# --- Navigation back link ---
st.markdown("[⬅ Back to main page](/Combined_Lunar_Database)", unsafe_allow_html=True)

