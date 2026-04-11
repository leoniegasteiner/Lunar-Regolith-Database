import streamlit as st
import pandas as pd



MISSION_NAME = "Luna 9" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Luna 9 Mission")
    if MISSION_NAME == "Luna 9":
        st.markdown("""<div style="text-align: justify;">
        Launched by the USSR, Luna 9 became the first spacecraft to achieve a survivable soft landing on the Moon on February 3, 1966. 
                    It landed near the rim of a crater in Oceanus Procellarum. 
                    <br><br>
                    While primarily a technology demonstrator, the mission proved that the lunar surface could support the weight of a lander, debunking "dust bowl" theories of the time.
                    Although Luna 9 lacked dedicated geotechnical instruments, it provided the first in-situ evidence of soil stability. 
                    Mechanical properties were inferred through visual analysis of the landing site via the onboard panoramic television system. 
                    Scientists estimated grain size distribution and surface morphology by observing the displacement of soil and the lack of significant sinkage of the lander’s 100kg capsule.
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