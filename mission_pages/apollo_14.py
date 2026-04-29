import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

MISSION_NAME = "Apollo 14"
# --- Page configuration ---
def show_mission(df):

    st.header("The Apollo 14 Mission")
    if MISSION_NAME == "Apollo 14":
        st.markdown(""" <div style="text-align: justify;">
    The Soil Mechanics Investigation conducted during the Apollo 14 mission aimed to obtain data on the composition, texture, and mechanical properties of the lunar soil, as well as their spatial variations.
    These data were used to formulate, verify, or refine existing theories on lunar surface processes and geological history.
    <br><br>
    The experiments relied on astronaut observations, in-situ photography, and post-mission examination of returned soil samples on Earth.
    In-situ measurements were performed using a penetrometer, which provided estimates of the internal friction angle, cohesion, and bulk density of the lunar soil.
    During one EVA, the astronauts also performed a trench experiment that allowed the determination of a lower bound for cohesion, assuming known values of density and internal friction angle.
    <br><br>
    A total of 13 kg of soil samples were collected using core tubes and returned to Earth.
    These samples were primarily analyzed for their chemical and geological properties, and no direct mechanical testing was performed.
    Additionally, the tracks of the Modular Equipment Transporter (MET) were analyzed to estimate the density and internal friction angle of the surface material under the assumption of a cohesionless soil.
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

    st.subheader("Apollo 14 Lunar Samples")
    st.markdown(""" The Apollo 14 mission landed on the Moon on February 5, 1971, and returned a total of 42.3 kg of lunar material to Earth.
                The samples included a large amount of rocks, and the investigations focused on the geological formation of the area of the landing site. 
                The samples were received and analyzed in the Lunar Receiving Laboratory (LRL).
                The table below lists all the samples returned from the Apollo 14 mission, based on the data available in the Apollo 14 rock samples technical report (I. Carlson, W. Walton, 1978, "Apollo 14 Rock Samples", JSC 14240).""")
    @st.cache_data
    def load_sample_data():
        df = pd.read_csv(
        "mission_pages/Apollo 14.csv",
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