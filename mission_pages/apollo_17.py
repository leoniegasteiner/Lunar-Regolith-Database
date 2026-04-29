import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


MISSION_NAME = "Apollo 17"
# --- Page configuration ---
def show_mission(df):

    st.header("The Apollo 17 Mission")
    st.write(""" <div style="text-align: justify;">
    The Soil Mechanics Investigation during the Apollo 17 mission was primarily passive, as no dedicated soil mechanics equipment was included.
    The results were therefore derived mainly from analysis of rover track patterns, astronaut observations, and photographic documentation of surface interactions.
    <br><br>
    The internal friction angle of the lunar soil was estimated from the geometry of rover tracks and astronaut footprints, assuming a known value for the bulk density of the surface material.
    These analyses provided qualitative confirmation of the soil’s mechanical properties as observed during previous missions.
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


    st.subheader("Apollo 17 Lunar Samples")
    st.markdown("""The Apollo 17 mission returned a total of 110.4 kg of lunar material, including a large amount of rocks and soil samples collected from the Taurus-Littrow region.
                The samples were received and analyzed in the Lunar Receiving Laboratory (LRL).
                The table below lists all the samples returned from the Apollo 17 mission, based on the data available in the Apollo 17 lunar sample information catalog (P. Butler, M.Duke, W.McCown,1973, "Apollo 17 Lunar Sample Information Catalog", Lunar Receiving Laboratory, MSC 03211).""")
    @st.cache_data
    def load_sample_data():
        df = pd.read_csv(
        "mission_pages/Apollo 17.csv",
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

    st.markdown("""The sample ID was assigned following a specific convention:
                
                Each sample is identified by a 5-digit number, where the first digit correspond to the mission number (7 for Apollo 17). 

                The Apollo 17 samples are grouped by sampling site, each group of one-thousand corresponds to an area around the lunar module.

                The first numbers for each area were used for drive tube, drill stems, and special samples. 

                The last digit is used to categorize soil samples based on their size: 
                * An unsieved reserve of each sample was kept and assigned a 0 as the unit digit (7WXY0), 
                * the fines smaller than 1mm were assigned a 1 (7WXY1), 
                * the fines between 1 and 2mm were assigned a 2 (7WXY2), 
                * the fines between 2 and 4mm were assigned a 3 (7WXY3), 
                * and the fines between 4 and 10mm were assigned a 4 (7WXY4). 
            
                Rocks from a documented bag are numbered 7WXY5 - 7WXY9 in order of decreasing size. 
                 
                """)