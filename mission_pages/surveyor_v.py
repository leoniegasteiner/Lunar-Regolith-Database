import streamlit as st
import pandas as pd

MISSION_NAME = "Surveyor V"

# --- Page configuration ---
def show_mission(df):

    st.header("The Surveyor V Mission")
    if MISSION_NAME == "Surveyor V":
        st.markdown("""<div style="text-align: justify;">
                    Surveyor V landed in Mare Tranquillitatis. 
                    Due to landing with two legs inside a rimless crater, the spacecraft rested at an angle of about $20^\circ$. 
                    This spacecraft included an Alpha Particle Backscattering Experiment, which provided the first-ever analysis of the lunar surface material's chemical composition. 
                    Data on mechanical properties were derived from analyzing the disturbances caused by the landing and from comparing pictures taken before and after firing the Vernier engines, which also allowed for studying the impact of engine exhaust on the material. 
                    The final results on cohesion and static bearing capability were obtained from the Vernier thrusters firing and footpad pattern analysis by assuming the angle of internal friction to be 35 degrees.
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