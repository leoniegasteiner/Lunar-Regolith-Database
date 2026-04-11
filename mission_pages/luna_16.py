import streamlit as st
import pandas as pd



MISSION_NAME = "Luna 16" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Luna 16 Mission")
    if MISSION_NAME == "Luna 16":
        st.markdown("""<div style="text-align: justify;">
                    Luna 16 was the first robotic mission to successfully return lunar soil samples to Earth, landing in Mare Fecunditatis in September 1970. 
                    It marked a shift from in-situ testing to detailed laboratory analysis of the regolith's physical characteristics.
                    <br><br>
                    The mission utilized an automatic rotary-percussive drill to extract a core sample to a depth of 35 cm. 
                    Upon return to Earth, the samples were analyzed within a controlled helium/nitrogen environment to prevent terrestrial contamination. 
                    Mechanical testing included compression tests and direct shear tests to determine internal friction angles and cohesion. 
                    The grain size distribution was also meticulously mapped, providing a baseline for mare-type regolith properties.
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