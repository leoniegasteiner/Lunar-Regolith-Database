import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

MISSION_NAME = "Apollo 15"
# --- Page configuration ---
def show_mission(df):

    st.header("The Apollo 15 Mission")
    if MISSION_NAME == "Apollo 15":
        st.markdown("""
    The Soil Mechanics Investigation conducted during the Apollo 15 mission benefited from an expanded set of instruments and tools to analyze the mechanical behavior of the lunar regolith.
    The crew was equipped with a self-recording penetrometer (SRP), core tubes for sample return, the Apollo Lunar Surface Drill (ALSD), and the Lunar Roving Vehicle (LRV).

    The SRP experiment provided in-situ measurements that allowed the determination of key mechanical parameters, including bulk density, internal friction angle, and cohesion.
    These data were compared with simulation results to validate soil models developed from previous missions. A trench test was also conducted by the Lunar Module Pilot to further assess the strength and stability of the surface material.

    A comparison of bulk density values obtained across the various Apollo missions, as analyzed by different experts, is presented in pages 7–23 of the mission report.
    No specific mechanical data are available for the samples returned to Earth from Apollo 15.
""")
        
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

    st.subheader("Apollo 15 Lunar Samples")
    st.markdown("""The Apollo 15 mission returned a total of 77 kg of lunar material, including a large amount of rocks and soil samples collected from the Hadley-Apennine region.
                The samples were received and analyzed in the Lunar Receiving Laboratory (LRL).
                The table below lists all the samples returned from the Apollo 15 mission, based on the data available in the Apollo 15 lunar sample information catalog (1971, "Lunar Sample Information Catalog Apollo 15", Lunar Receiving Laboratory, MSC 03209).""")
    @st.cache_data
    def load_sample_data():
        df = pd.read_csv(
        "mission_pages/Apollo 15.csv",
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
    st.markdown(""" The sample ID was assigned following a specific convention:

                Each sample is identified by a 5-digit number, where the first two digits correspond to the mission number (15 for Apollo 15).

                The last three digits indicate the sample type and allow to group samples by collection location.

                The first 14 numbers (15001 - 15014) were assigned to Drill stems, drive tubes, and special environment sample containers (SESC).

                The last samples (15900 - 15999) are the samples that are not easily categorized such as dust sweepings and material caught on filters, etc.

                The materials from the rakes and the soil samples were assigned the numbers 15100 - 15199, 15300 - 15399, and 15600 - 15699.

                Whithin these samples, the fines are categorized based on their size through their unit digit:
                * An unsieved reserve of each sample was kept and assigned a 0 as the unit digit (15XY0), 
                * the fines smaller than 1mm were assigned a 1 (15XY1), 
                * the fines between 1 and 2mm were assigned a 2 (15XY2), 
                * the fines between 2 and 4mm were assigned a 3 (15XY3), 
                * and the fines between 4 and 10mm were assigned a 4 (15XY4).

                The remaining IDs correspond to rocks.""")