import streamlit as st
import pandas as pd
import plotly.express as px

MISSION_NAME = "Apollo 12"
# --- Page configuration ---
def show_mission(df):

    st.header("The Apollo 12 Mission")
    if MISSION_NAME == "Apollo 12":
        st.markdown("""
    <div style="text-align: justify;">
    The Soil Mechanics Investigation conducted during the Apollo 12 mission had objectives similar to those of Apollo 11, with a focus on characterizing the mechanical behavior of the lunar regolith and assessing its interaction with the lunar module during landing.
    <br><br>
    Comparative analysis of descent films from Apollo 11 and Apollo 12 provided valuable data on the response of the lunar surface to engine exhaust and landing forces. Penetration of the lunar module’s footpads into the surface allowed computation of static bearing pressures, offering further insight into the bearing capacity and strength characteristics of the soil at the landing site.
    <br><br>
    Samples were collected using a core tube sampler and returned to Earth for laboratory testing. These tests aimed to determine basic mechanical properties, including bulk density and cohesion. However, only a limited number of mechanical experiments were performed on the returned samples, and therefore the data obtained from Apollo 12 provide only partial information on the mechanical behavior of the lunar regolith.
    </div>""", unsafe_allow_html=True)
        
    st.subheader(f"Lunar regolith data from the {MISSION_NAME} mission")
    
    mission_data = df[df["Mission"].str.strip() == MISSION_NAME]
    if mission_data.empty:
        st.warning(f"No specific regolith data found for the mission: {MISSION_NAME}.")
    else:
        columns_to_display = [
        "Mission", "Location", "Terrain","Year","Type of mission","Test", "Test location", "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Bearing capacity (kPa)", "Normal stress range (kPa)", "Void ratio", "Density of grains (g/cm^3)", "Compressibility Coefficient", "Depth (cm)", "Porosity (%)", "Force applied (N)", "Source","Year of publication", "DOI / URL","Comments"]
        available_columns = [col for col in columns_to_display if col in mission_data.columns]
        st.dataframe(
            mission_data[available_columns],
            use_container_width=True
        )

#    # --- Data and plot ---
#    st.header("Lunar Regolith Density Variation with Depth")
#
#    # No numeric data available
#    data = pd.DataFrame({
#        "Testing Method": [],
#        "Depth (cm)": [],
#        "Density (g/cm³)": []
#    })
#
#    # --- Plot or message ---
#    if data.empty:
#        st.info("No quantitative density–depth data available for the Apollo 12 mission.")
#    else:
#        fig = px.line(
#            data,
#            x="Depth (cm)",
#            y="Density (g/cm³)",
#            color="Testing Method",
#            title="Density vs Depth",
#            markers=True
#        )
#        st.plotly_chart(fig, use_container_width=True)
#
#
#