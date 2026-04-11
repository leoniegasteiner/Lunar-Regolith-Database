import streamlit as st
import pandas as pd



MISSION_NAME = "Luna 17" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Luna 17 Mission")
    if MISSION_NAME == "Luna 17":
        st.markdown("""<div style="text-align: justify;">
                    Luna 17 delivered Lunokhod 1, the first remote-controlled robot to explore the lunar surface, to Mare Imbrium in November 1970. 
                    As a mobile laboratory, it allowed for the mapping of mechanical properties across a traverse of over 10 km.
                    <br><br>
                    Lunokhod 1 was equipped with a PrOP (Instrument for Cross-Country Capability) device. 
                    This consisted of a cone-vane penetrometer that performed over 500 tests. 
                    The bearing capacity was calculated by measuring the vertical force required to press the cone into the soil, while shear resistance was determined by rotating the vane and measuring the required torque. 
                    Average shear strength was recorded, providing crucial data on how regolith behaves under the load of moving wheels.
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