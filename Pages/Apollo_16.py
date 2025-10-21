import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page configuration ---
def show_mission():
    st.set_page_config(page_title="Apollo 16 Lunar Regolith Data", initial_sidebar_state="collapsed")

    st.title("Apollo 16 Lunar Regolith Data")

    st.header("The Apollo 16 Mission")
    st.write("""
    The Soil Mechanics Investigation during the Apollo 16 mission involved both in-situ measurements and observational analyses of the lunar surface.
    A penetrometer was used to obtain direct measurements of soil resistance, while additional data were gathered from visual observations of interactions between the soil and the rover wheels, drive tube insertions, and deep drill samples collected for return to Earth.

    The stability of the soil during drilling operations was also analyzed to estimate the cohesion of the regolith, assuming a known value for the internal friction angle.
    These combined observations provided further insight into the mechanical behavior and strength characteristics of the lunar surface material at the Apollo 16 landing site.
    """)

    # --- Data and plot ---
    st.header("Lunar Regolith Density Variation with Depth")

    data = pd.DataFrame({
        "Testing Method": [
            "Drive tube", "Drive tube", "Drive tube", "Drive tube", "Drive tube", "Drive tube", "Drive tube",
            "Drill stem", "Drill stem", "Drill stem", "Drill stem", "Drill stem",
            "Penetrometer", "Penetrometer", "Penetrometer", "Penetrometer", "Penetrometer", "Penetrometer", "Penetrometer", "Penetrometer",
            "Footprint analysis", "Footprint analysis", "Footprint analysis", "Footprint analysis", "Footprint analysis", "Footprint analysis"
        ],
        "Depth range (cm)": [
            "0-32", "32-65", "0-28", "29-63", "0-32", "32-66", "0-27",
            "0-223", "0-223", "0-223", "0-223", "0-223",
            "0-8", "0-25", "0-25", "0-5", "0-5", "0-20", "0-25", "0-25",
            "0-10", "0-10", "0-10", "0-10", "0-10", "0-10"
        ],
        "Density (g/cm³)": [
            1.47, 1.72, 1.48, 1.63, 1.39, 1.66, 1.59,
            1.46, 1.43, 1.56, 1.66, 1.75,
            2.04, 1.97, 1.97, 1.68, 1.71, 1.89, 1.77, 1.87,
            1.73, 1.67, 1.69, 1.69, 1.68, 1.73
        ],
        "Porosity (%)": [
            52, 43.5, 51.5, 46.5, 53.5, 45.5, 48,
            52, 53, 49, 45.5, 42.5,
            33, 33.5, 35.5, 45, 44, 38, 42, 39,
            43.1, 45.2, 44.8, 44.8, 45.0, 43.7
        ],
        "Force Applied (N)": ["NA"] * 26
    })

    # --- Convert depth ranges into numeric start/end points ---
    expanded_data = []
    for _, row in data.iterrows():
        try:
            start, end = map(float, row["Depth range (cm)"].split("-"))
            expanded_data.append({
                "Depth (cm)": start,
                "Density (g/cm³)": row["Density (g/cm³)"],
                "Testing Method": row["Testing Method"]
            })
            expanded_data.append({
                "Depth (cm)": end,
                "Density (g/cm³)": row["Density (g/cm³)"],
                "Testing Method": row["Testing Method"]
            })
        except Exception:
            pass

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
    fig.update_yaxes(autorange="reversed")  # optional: deeper = downward
    st.plotly_chart(fig, use_container_width=True)

    # --- Navigation back link ---
    st.markdown("[⬅ Back to main page](/Combined_Lunar_Database)", unsafe_allow_html=True)
