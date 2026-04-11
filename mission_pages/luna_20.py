import streamlit as st
import pandas as pd



MISSION_NAME = "Luna 20" 

# --- Page configuration ---
def show_mission(df):
    st.header("The Luna 20 Mission")
    if MISSION_NAME == "Luna 20":
        st.markdown("""<div style="text-align: justify;">
                    In February 1972, Luna 20 landed in the rugged Apollonius highland region. 
                    This mission was a direct counterpart to Luna 16, designed to provide a comparative analysis between the mechanical properties of lunar highlands versus the previously sampled maria.
                    <br><br>
                    Similar to Luna 16, a core sample was extracted via a rotary-percussive drill. 
                    Because the highland regolith was significantly more resistant and abrasive than mare soil, the drilling process provided indirect data on the soil's mechanical resistance. 
                    The returned samples were subjected to the same terrestrial laboratory shear and compression tests as the Luna 16 samples, revealing that highland regolith generally possesses a higher degree of compaction and different grain morphology.
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