import streamlit as st
import pandas as pd



MISSION_NAME = "Luna 21" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Luna 21 Mission")
    if MISSION_NAME == "Luna 21":
        st.markdown("""<div style="text-align: justify;">
                    Luna 21 deployed Lunokhod 2 in the Le Monnier crater in January 1973. 
                    This mission aimed to explore the transition zone between a mare and a highland area.
                    <br><br>
                    While Lunokhod 2 focused heavily on chemical and magnetic analysis, it continued to collect mechanical data via its wheels and the PrOP penetrometer system.
                    By analyzing the "slip" of the wheels and the depth of the tracks via onboard cameras, researchers could infer the soil's traction and deformation characteristics. 
                    Although it performed fewer dedicated penetrometer tests than its predecessor, the data obtained was vital for understanding the mechanical variability of the lunar "coastline" regions.
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