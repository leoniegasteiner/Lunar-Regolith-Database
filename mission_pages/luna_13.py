import streamlit as st
import pandas as pd



MISSION_NAME = "Luna 13" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Luna 13 Mission")
    if MISSION_NAME == "Luna 13":
        st.markdown("""<div style="text-align: justify;">
                    Luna 13 landed in the Mare Imbrium region on December 24, 1966. 
                    Building on the success of Luna 9, this mission was specifically designed to conduct the first direct physical measurements of the lunar soil's mechanical strength and density.
                    <br><br>
                    The lander deployed two specialized booms containing a mechanical penetrometer and a radiation densimeter. 
                    The penetrometer used a spring-loaded explosive charge to drive a titanium conical indentor into the regolith to a depth of approximately 45 mm, allowing for the calculation of bearing capacity. 
                    Simultaneously, the radiation densimeter used gamma-ray scattering to determine the bulk density of the upper 15 cm of soil. 
                    Additionally, a dynamograph recorded the impact forces during landing to estimate the soil’s dynamic resistance.    
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