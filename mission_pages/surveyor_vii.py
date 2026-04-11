import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

MISSION_NAME = "Surveyor VII"

# --- Page configuration ---
def show_mission(df):

    st.header("The Surveyor VII Mission")
    if MISSION_NAME == "Surveyor VII":
        st.markdown("""<div style="text-align: justify;">
    Surveyor VII was the final mission, landing at the rim of the Tycho crater, a highland area. 
                    It carried the most advanced science payload, including the Alpha Particle Backscattering Experiment and the Surface Sampler. 
                    Spacecraft touchdown analysis (using TV pictures and telemetry) determined the bearing capacity and general soil behavior. 
                    The Surface Sampler was extensively used to analyze mechanical properties by performing trench experiments, a series of 16 bearing tests (pushing/dragging and measuring motor current), and even impact experiments by dropping rocks. 
                    These mechanical tests also served to prepare samples (disturbed and undisturbed soil) for the alpha scattering experiment.        
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