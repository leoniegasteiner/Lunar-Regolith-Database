import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

MISSION_NAME = "Apollo 16"

def show_mission(df):

    st.header("The Apollo 16 Mission")
    if MISSION_NAME == "Apollo 16":
        st.markdown("""<div style="text-align: justify;">
            The Soil Mechanics Investigation during the Apollo 16 mission involved both in-situ measurements and observational analyses of the lunar surface. 
            A penetrometer was used to obtain direct measurements of soil resistance, while additional data were gathered from visual observations of interactions between the soil and the rover wheels, drive tube insertions, and deep drill samples collected for return to Earth.
            The stability of the soil during drilling operations was also analyzed to estimate the cohesion of the regolith, assuming a known value for the internal friction angle. 
            These combined observations provided further insight into the mechanical behavior and strength characteristics of the lunar surface material at the Apollo 16 landing site.
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

    st.subheader("Apollo 16 Lunar Samples")
    st.markdown("""The Apollo 16 mission returned a total of 95.7 kg of lunar material, including a large amount of rocks and soil samples collected from the Descartes Highlands region.
                The samples were received and analyzed in the Lunar Receiving Laboratory (LRL).
                The table below lists all the samples returned from the Apollo 16 mission, based on the data available in the Apollo 16 lunar sample information catalog (P. Butler, M. Duke, W. McCown, 1972, "Lunar Sample Information Catalog Apollo 16", Lunar Receiving Laboratory, MSC 03210).""")
    @st.cache_data
    def load_sample_data():
        df = pd.read_csv(
        "mission_pages/Apollo 16.csv",
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
                
                Each sample is identified by a 5-digit number, where the first digit is the mission designation (6 for Apollo 16). 

                The Apollo 16 samples are grouped by sampling site, each group of one-thousand corresponds to an area around the lunar module. 

                The first numbers for each area were used for drive tube, drill stems, and special samples. 

                Documented bags (DB) with predominantly soil samples were assigned even number decades.

                The last digit is used to categorize soil samples based on their size: 
                * An unsieved reserve of each sample was kept and assigned a 0 as the unit digit (6WXY0), 
                * the fines smaller than 1mm were assigned a 1 (6WXY1), 
                * the fines between 1 and 2mm were assigned a 2 (6WXY2), 
                * the fines between 2 and 4mm were assigned a 3 (6WXY3), 
                * and the fines between 4 and 10mm were assigned a 4 (6WXY4). 
                
                Rocks from a documented bag are numbered 6WXY5 - 6WXY9 in order of decreasing size. 
                 """)