import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page configuration ---
def show_mission():
    st.set_page_config(page_title="Apollo 15 Lunar Regolith Data", initial_sidebar_state="collapsed")
    
    st.title("Apollo 15 Lunar Regolith Data")
    
    st.header("The Apollo 15 Mission")
    st.write("""
    The Soil Mechanics Investigation conducted during the Apollo 15 mission benefited from an expanded set of instruments and tools to analyze the mechanical behavior of the lunar regolith.
    The crew was equipped with a self-recording penetrometer (SRP), core tubes for sample return, the Apollo Lunar Surface Drill (ALSD), and the Lunar Roving Vehicle (LRV).
    
    The SRP experiment provided in-situ measurements that allowed the determination of key mechanical parameters, including bulk density, internal friction angle, and cohesion.
    These data were compared with simulation results to validate soil models developed from previous missions. A trench test was also conducted by the Lunar Module Pilot to further assess the strength and stability of the surface material.
    
    A comparison of bulk density values obtained across the various Apollo missions, as analyzed by different experts, is presented in pages 7–23 of the mission report.
    No specific mechanical data are available for the samples returned to Earth from Apollo 15.
    """)
    
    # --- Data and plot ---
    st.header("Lunar Regolith Density Variation with Depth")
    
    data = pd.DataFrame({
        "Testing Method": [
            "Drive tube", "Drive tube", "Drive tube", "Drive tube", "Drive tube",
            "Drill stem", "Drill stem", "Drill stem", "Drill stem", "Drill stem", "Drill stem",
            "Penetrometer"
        ],
        "Depth range (cm)": [
            "0-35", "35-70", "0-35", "0-23", "23-68",
            "0-236", "0-236", "0-236", "0-236", "0-236", "0-236",
            "0-20"
        ],
        "Density (g/cm³)": [
            "1.36", "1.64-1.69", "1.35", "1.69", "1.79-1.91",
            "1.62-1.96", "1.84", "1.75", "1.79", "1.62", "2.15",
            "NA"
        ]
    })
    
    # --- Expand depth and density ranges ---
    expanded_data = []
    for _, row in data.iterrows():
        # Handle depth range
        try:
            start_d, end_d = map(float, row["Depth range (cm)"].split("-"))
        except Exception:
            start_d, end_d = (0.0, 0.0)
    
        # Handle density range
        density_str = str(row["Density (g/cm³)"])
        if "-" in density_str:
            try:
                start_rho, end_rho = map(float, density_str.split("-"))
                rho = (start_rho + end_rho) / 2  # use midpoint for plotting
            except Exception:
                rho = None
        else:
            try:
                rho = float(density_str)
            except ValueError:
                rho = None
    
        if rho is not None:
            expanded_data.append({"Depth (cm)": start_d, "Density (g/cm³)": rho, "Testing Method": row["Testing Method"]})
            expanded_data.append({"Depth (cm)": end_d, "Density (g/cm³)": rho, "Testing Method": row["Testing Method"]})
    
    expanded_df = pd.DataFrame(expanded_data).sort_values(by="Depth (cm)")
    
    # --- Plot ---
    fig = px.line(
        expanded_df,
        x="Depth (cm)",
        y="Density (g/cm³)",
        color="Testing Method",
        title="Lunar Regolith Density Profile with Depth",
        markers=True
    )
    fig.update_yaxes(autorange="reversed")  # optional, if you prefer deeper = downward
    st.plotly_chart(fig, use_container_width=True)
    
    # --- Navigation back link ---
    st.markdown("[⬅ Back to main page](/Combined_Lunar_Database)", unsafe_allow_html=True)
    