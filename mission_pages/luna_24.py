import streamlit as st
import pandas as pd



MISSION_NAME = "Luna 24" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Luna 24 Mission")
    if MISSION_NAME == "Luna 24":
        st.markdown("""<div style="text-align: justify;">
                    The final mission of the Soviet Luna program, Luna 24, landed in Mare Crisium in August 1976. 
                    Its primary goal was a deep-core sampling of the regolith to study the vertical stratigraphy of the lunar surface.
                    <br><br>
                    The mission employed a sophisticated "thin-walled" rotary drill capable of reaching a depth of 225 cm. 
                    The mechanical effort required to penetrate to this depth provided significant data on the relative density and porosity of the deeper regolith layers. 
                    While post-return analysis focused largely on geochemistry, the core's ability to maintain its structure during extraction offered critical insights into the natural packing and cohesion of regolith at depths exceeding two meters.
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