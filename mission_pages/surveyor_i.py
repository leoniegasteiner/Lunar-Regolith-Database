import streamlit as st
import pandas as pd



MISSION_NAME = "Surveyor I" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Surveyor I Mission")
    if MISSION_NAME == "Surveyor I":
        st.markdown("""<div style="text-align: justify;">
        Surveyor I was the first successful American lunar lander, launched on May 30, 1966. Its primary objective was to demonstrate the engineering capabilities required for a soft-landing on the moon. Secondary objectives included obtaining engineering data on spacecraft performance during flight and on the lunar surface, capturing TV images of the lunar surface, and acquiring data on radar reflectivity, bearing strength of lunar regolith, and spacecraft temperatures. 
    While not equipped with direct scientific analysis instruments, the mission obtained critical data through its TV system and many onboard sensors. Analysis of the appearance of the lunar surface near the footpads and the rim of the impact depression allowed to determine the nature of the lunar regolith as a granular material. The static bearing capacity was calculated from the depth of footpad penetration, which, based on an assumed bulk density, allowed for the estimation of possible ranges for cohesion and the angle of internal friction.
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