import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

MISSION_NAME = "Surveyor III"
# --- Page configuration ---
def show_mission(df):

    st.header("The Surveyor III Mission")
    if MISSION_NAME == "Surveyor III":
        st.markdown("""<div style="text-align: justify;">
                    Surveyor III was the second successful mission, landing in the mare region of Oceanus Procellarum. 
                    The spacecraft was similar to its predecessor, but notably carried the Soil Mechanics Surface Sampler (SMSS), an articulated arm with a scoop, specifically designed for soil mechanics experiments. 
                    <br><br>
                    Although the landing involved three separate touchdowns due to engine issues, the load distribution on the footpads was recorded, as with Surveyor I. 
                    The SMSS performed various tests, including scooping, scraping, and trench experiments, and a series of 8 bearing tests using the scoop. 
                    The results of the SMSS tests were combined with the footpad penetration analysis to calculate values for cohesion, porosity, and angle of internal friction. 
                    The resulting property values differed from those of Surveyor I, which was attributed to the fact that the SMSS tests were likely performed on the rim of a crater due to the spacecraft's landing position.
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
