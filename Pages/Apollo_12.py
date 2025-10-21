import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page configuration ---
st.set_page_config(page_title="Apollo 12 Lunar Regolith Data", initial_sidebar_state="collapsed")

st.title("Apollo 12 Lunar Regolith Data")

st.header("The Apollo 12 Mission")
st.write("""
The Soil Mechanics Investigation conducted during the Apollo 12 mission had objectives similar to those of Apollo 11, with a focus on characterizing the mechanical behavior of the lunar regolith and assessing its interaction with the lunar module during landing.
         
Comparative analysis of descent films from Apollo 11 and Apollo 12 provided valuable data on the response of the lunar surface to engine exhaust and landing forces. Penetration of the lunar module’s footpads into the surface allowed computation of static bearing pressures, offering further insight into the bearing capacity and strength characteristics of the soil at the landing site.

Samples were collected using a core tube sampler and returned to Earth for laboratory testing. These tests aimed to determine basic mechanical properties, including bulk density and cohesion. However, only a limited number of mechanical experiments were performed on the returned samples, and therefore the data obtained from Apollo 12 provide only partial information on the mechanical behavior of the lunar regolith.
""")

# --- Data and plot ---
st.header("Lunar Regolith Density Variation with Depth")

# No numeric data available
data = pd.DataFrame({
    "Testing Method": [],
    "Depth (cm)": [],
    "Density (g/cm³)": []
})

# --- Plot or message ---
if data.empty:
    st.info("No quantitative density–depth data available for the Apollo 12 mission.")
else:
    fig = px.line(
        data,
        x="Depth (cm)",
        y="Density (g/cm³)",
        color="Testing Method",
        title="Density vs Depth",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Navigation back link ---
st.markdown("[⬅ Back to main page](/Combined_Lunar_Database)", unsafe_allow_html=True)
