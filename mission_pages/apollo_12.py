import streamlit as st
import pandas as pd
import plotly.express as px

MISSION_NAME = "Apollo 12"
# --- Page configuration ---
def show_mission(df):

    st.header("The Apollo 12 Mission")
    if MISSION_NAME == "Apollo 12":
        st.markdown("""
    <div style="text-align: justify;">
    The Soil Mechanics Investigation conducted during the Apollo 12 mission had objectives similar to those of Apollo 11, with a focus on characterizing the mechanical behavior of the lunar regolith and assessing its interaction with the lunar module during landing.
    <br><br>
    Comparative analysis of descent films from Apollo 11 and Apollo 12 provided valuable data on the response of the lunar surface to engine exhaust and landing forces. Penetration of the lunar module’s footpads into the surface allowed computation of static bearing pressures, offering further insight into the bearing capacity and strength characteristics of the soil at the landing site.
    <br><br>
    Samples were collected using a core tube sampler and returned to Earth for laboratory testing. These tests aimed to determine basic mechanical properties, including bulk density and cohesion. However, only a limited number of mechanical experiments were performed on the returned samples, and therefore the data obtained from Apollo 12 provide only partial information on the mechanical behavior of the lunar regolith.
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

    st.subheader("Apollo 12 Lunar Samples")
    st.markdown("""The Apollo 12 mission landed on the Moon on the 19th of November 1969, and returned a total of 34.35 kg of Lunar material to Earth. 
                The samples included a contingency sample of 1.9 kg containing loose material scooped from the surface, a selected sample of 14.8 kg including loose material and a drive tube, 
                a documented sample of 11 kg with different types of rocks and soil collected for different experiments, including a double core tube sample and a unopened drive tube, and a tote-bag sample containing 6.6 kg of soil and rocks. 
                The samples were received and analyzed in the Lunar Receiving Laboratory (LRL). 
                The table below lists all the samples returned from the Apollo 12 mission, based on the data available in the Apollo 12 Lunar Sample Information technical report from NASA (J. Warner, 1970, "Apollo 12 Lunar-Sample Information, NASA TR R-353).""")
    @st.cache_data
    def load_sample_data():
        df = pd.read_csv(
        "mission_pages/Apollo 12.csv",
        sep=";",
        dtype=str,
        header=0,
        skip_blank_lines=False,
        )
        df.columns =  ["Sample ID", "Serial Number", "Return Container", "Container", "Sample Type", "Weight (g)"]
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
        return df

    samples_data = load_sample_data()

    st.dataframe(samples_data)