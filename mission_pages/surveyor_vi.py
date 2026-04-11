import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

MISSION_NAME = "Surveyor VI"

# --- Page configuration ---
def show_mission(df):

    st.header("The Surveyor VI Mission")
    if MISSION_NAME == "Surveyor VI":
        st.markdown("""<div style="text-align: justify;">
    Surveyor VI was a duplicate of Surveyor V, landing in Sinus Medii, a flat mare area. 
                    The data on regolith properties were once again obtained through spacecraft touchdown analysis for bearing capacity computation, and Vernier thruster firing to study material erosion. 
                    The Vernier engines were fired long enough for the spacecraft to hop off the lunar surface briefly. A value for cohesion was determined from estimated shear stress values caused by the Vernier engine firing. 
                    The overall analysis derived from telemetry and pictures confirmed that the bearing strength increases with depth, and cohesion was estimated through two methods: Vernier engine firing and attitude control jet firing.         
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