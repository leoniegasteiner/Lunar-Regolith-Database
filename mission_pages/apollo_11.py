import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from mission_pages.surveyor_v import MISSION_NAME

MISSION_NAME = "Apollo 11"
# --- Page configuration ---
def show_mission(df):

    st.header("The Apollo 11 Mission")
    if MISSION_NAME == "Apollo 11":
        st.markdown("""
        <div style="text-align: justify;">
    The Apollo 11 lunar lander touched down on the Moon on July 20 1969. 
    The primary objectives of the mission were to land men on the Lunar surface, collect lunar material samples, and return the crew safely to Earth.
    Specific scientific objectives of the Soil Mechanics Investigation at the Apollo 11 landing site included the following:
    to verify lunar soil models previously formulated from Earth-based observations, laboratory investigations, and data from lunar orbiting and unmanned landing missions.
    <br><br>
    The Soil Mechanics Investigation pursued several engineering objectives: to obtain information on the interaction between the lunar module (LM) and the lunar surface during landing, to provide a basis for altering mission plans in response to unexpected surface conditions; to assess the effect of lunar soil properties on astronaut and surface vehicle mobility; and to gather at least qualitative information necessary for the deployment, installation, operation, and maintenance of scientific and engineering equipment for extended lunar exploration.
    <br><br>
    Because no specific hardware could be added to the spacecraft for soil mechanics analysis, existing tools were repurposed from other experiments. These included astronaut and camera observations, spacecraft flight mechanics telemetry data, and various tools and poles inserted into the ground to observe its behavior.
    <br><br>
    Core tube samples were brought back to Earth for laboratory analysis in the Lunar Regolith Laboratory. Testing of these samples with a penetrometer made it possible to determine a compressed bulk density and a range of cohesion values, providing the first direct mechanical characterization of lunar soil.
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

    st.subheader("Apollo 11 Lunar Samples")
    st.markdown(""" the Apollo 11 mission returned a total of 21.55 kg of lunar material, representing the first documented rock samples brough back from an extraterrestial body.
                The samples were received and analyzed in the Lunar Receiving Laboratory (LRL). A re-examination of the samples was done in 1977, applying the knowledge earned during the five subsequent Apollo missions.
                The contingency sample of the mission was collected by scooping loose material from the surface near the lunar module into a bag. 
                The bulk sample consisted of 15kg of soil and rocks scooped into a container, and the documented sample consisted of approximately 20 samples picked up by the astronaut. 
                Additionally to the rocks, the documented sample included two drive tubes that were inserted into the lunar surface using a hammer.
                The table below includes information on the lunar samples returned from the Apollo 11 mission, based on the data available in the revised Apollo 11 lunar sample catalog (F.E. Kramer, D.B. Twendell, and W.J.A Walton, 1977, "Apollo-11 Lunar Sample Catalogue (Revised), JSC12522). """)
    @st.cache_data
    def load_sample_data():
        df = pd.read_csv(
        "mission_pages/Apollo 11.csv",
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