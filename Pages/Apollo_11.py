import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page configuration ---
def show_mission():
    st.set_page_config(page_title="Apollo 11 Lunar Regolith Data", initial_sidebar_state="collapsed")
    
    st.title("Apollo 11 Lunar Regolith Data")
    
    st.header("The Apollo 11 Mission")
    st.write("""
    Specific scientific objectives of the Soil Mechanics Investigation at the Apollo 11 landing site included the following:
    to verify lunar soil models previously formulated from Earth-based observations, laboratory investigations, and data from lunar orbiting and unmanned landing missions.
    
    The Soil Mechanics Investigation pursued several engineering objectives: to obtain information on the interaction between the lunar module (LM) and the lunar surface during landing, to provide a basis for altering mission plans in response to unexpected surface conditions; to assess the effect of lunar soil properties on astronaut and surface vehicle mobility; and to gather at least qualitative information necessary for the deployment, installation, operation, and maintenance of scientific and engineering equipment for extended lunar exploration.
    
    Because no specific hardware could be added to the spacecraft for soil mechanics analysis, existing tools were repurposed from other experiments. These included astronaut and camera observations, spacecraft flight mechanics telemetry data, and various tools and poles inserted into the ground to observe its behavior.
    
    Core tube samples were brought back to Earth for laboratory analysis in the Lunar Regolith Laboratory. Testing of these samples with a penetrometer made it possible to determine a compressed bulk density and a range of cohesion values, providing the first direct mechanical characterization of lunar soil.
    """)
    
    # --- Data and plot ---
    st.header("Lunar Regolith Density Variation with Depth")
    
    # Data
    data = pd.DataFrame({
        "Testing Method": ["Penetrometer", "Penetrometer", "Penetrometer", "Core Tube"],
        "Depth (cm)": [2, 2, 2, 10],
        "Density (g/cm³)": [1.36, 1.77, 1.80, 1.66],
        "Porosity (%)": [None, None, None, 46.5],
        "Force Applied (N)": [1.82, 10.5, 54.5, None]
    })
    
    # Plot
    fig = px.line(
        data,
        x="Depth (cm)",
        y="Density (g/cm³)",
        color="Testing Method",
        title="Density vs Depth",
        markers=True
    )
    fig.update_layout(
        xaxis_title="Depth (cm)",
        yaxis_title="Density (g/cm³)",
        legend_title="Testing Method"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Navigation back link ---
    st.markdown("[⬅ Back to main page](/Combined_Lunar_Database)", unsafe_allow_html=True)
    