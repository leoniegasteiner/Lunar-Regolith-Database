import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        "Density (g/cm³)": [None, None, 1.75],
        "Porosity (%)": ["NA"] * 3,
        "Force Applied (N)": ["71-134", "134-223", None]
    })

    # --- Sidebar ---
    methods_selected = st.multiselect("Select Testing Method(s)", data["Testing Method"].unique(), default=data["Testing Method"].unique())
    value_to_plot = st.radio("Value to plot", ["Density (g/cm³)", "Porosity (%)", "Force Applied (N)"])
    filtered_data = data[data["Testing Method"].isin(methods_selected)].copy()

    # --- Prepare bars ---
    bars = []
    color_map = {method: px.colors.qualitative.Plotly[i % 10] for i, method in enumerate(filtered_data["Testing Method"].unique())}

    for _, row in filtered_data.iterrows():
        # Depth
        try:
            depth_start, depth_end = map(float, row["Depth range (cm)"].split("-"))
        except:
            continue

        # Value handling
        val_str = str(row[value_to_plot])
        if val_str.upper() == "NA":
            continue
        if "-" in val_str:
            try:
                val_start, val_end = map(float, val_str.split("-"))
            except:
                continue
        else:
            val_start = val_end = float(val_str)

        # Rectangle for each bar (x = value range, y = depth range)
        bars.append(go.Scatter(
            x=[val_start, val_end, val_end, val_start, val_start],
            y=[depth_start, depth_start, depth_end, depth_end, depth_start],
            fill="toself",
            fillcolor=color_map[row["Testing Method"]],
            line=dict(color=color_map[row["Testing Method"]], width=2),  # outline matches method color
            opacity=0.5,
            name=row["Testing Method"],
            hoverinfo='text',
            hovertext=f"Method: {row['Testing Method']}<br>{value_to_plot}: {val_start}-{val_end}<br>Depth: {depth_start}-{depth_end} cm",
            showlegend=False
        ))

    fig = go.Figure(bars)

    # Manual legend for methods
    for method, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color, line=dict(color=color, width=2)),
            name=method,
            showlegend=True
        ))

    fig.update_layout(
        title=f"{value_to_plot} vs Depth",
        xaxis_title=value_to_plot,
        yaxis_title="Depth (cm)",
        yaxis=dict(autorange="reversed"),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)