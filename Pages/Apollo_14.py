import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page configuration ---
def show_mission():
    st.set_page_config(page_title="Apollo 14 Lunar Regolith Data", initial_sidebar_state="collapsed")
    
    st.title("Apollo 14 Lunar Regolith Data")
    
    st.header("The Apollo 14 Mission")
    st.write("""
    The Soil Mechanics Investigation conducted during the Apollo 14 mission aimed to obtain data on the composition, texture, and mechanical properties of the lunar soil, as well as their spatial variations.
    These data were used to formulate, verify, or refine existing theories on lunar surface processes and geological history.
    
    The experiments relied on astronaut observations, in-situ photography, and post-mission examination of returned soil samples on Earth.
    In-situ measurements were performed using a penetrometer, which provided estimates of the internal friction angle, cohesion, and bulk density of the lunar soil.
    During one EVA, the astronauts also performed a trench experiment that allowed the determination of a lower bound for cohesion, assuming known values of density and internal friction angle.
    
    A total of 13 kg of soil samples were collected using core tubes and returned to Earth.
    These samples were primarily analyzed for their chemical and geological properties, and no direct mechanical testing was performed.
    Additionally, the tracks of the Modular Equipment Transporter (MET) were analyzed to estimate the density and internal friction angle of the surface material under the assumption of a cohesionless soil.
    """)
    
    # --- Data and plot ---
    st.header("Lunar Regolith Density Variation with Depth")
    
    data = pd.DataFrame({
        "Testing Method": ["Penetrometer", "Penetrometer", "Core tube"],
        "Depth range (cm)": ["0-44", "0-62", "0-36"],
        "Density (g/cm³)": ["NA", "NA", "1.75"],
        "Force Applied (N)": ["71-134", "134-223", "NA"]
    })
    
    # --- Expand numeric ranges ---
    expanded_data = []
    for _, row in data.iterrows():
        # Parse depth range
        try:
            start_d, end_d = map(float, row["Depth range (cm)"].split("-"))
        except Exception:
            start_d, end_d = (0.0, 0.0)
    
        # Parse density
        density_str = str(row["Density (g/cm³)"])
        if "-" in density_str:
            try:
                start_rho, end_rho = map(float, density_str.split("-"))
                rho = (start_rho + end_rho) / 2
            except Exception:
                rho = None
        else:
            try:
                rho = float(density_str)
            except ValueError:
                rho = None
    
        if rho is not None:
            expanded_data.append({
                "Depth (cm)": start_d,
                "Density (g/cm³)": rho,
                "Testing Method": row["Testing Method"]
            })
            expanded_data.append({
                "Depth (cm)": end_d,
                "Density (g/cm³)": rho,
                "Testing Method": row["Testing Method"]
            })
    
    expanded_df = pd.DataFrame(expanded_data).sort_values(by="Depth (cm)")
    
    # --- Plot ---
    if not expanded_df.empty:
        fig = px.line(
            expanded_df,
            x="Depth (cm)",
            y="Density (g/cm³)",
            color="Testing Method",
            title="Lunar Regolith Density Profile with Depth",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numerical density data available for plotting.")
    
    # --- Navigation back link ---
    st.markdown("[⬅ Back to main page](/Combined_Lunar_Database)", unsafe_allow_html=True)
    