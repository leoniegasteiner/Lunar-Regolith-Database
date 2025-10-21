import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# --- Page configuration ---
def show_mission():
    st.set_page_config(page_title="Apollo 17 Lunar Regolith Data", initial_sidebar_state="collapsed")

    st.title("Apollo 17 Lunar Regolith Data")

    st.header("The Apollo 17 Mission")
    st.write("""
    The Soil Mechanics Investigation during the Apollo 17 mission was primarily passive, as no dedicated soil mechanics equipment was included.
    The results were therefore derived mainly from analysis of rover track patterns, astronaut observations, and photographic documentation of surface interactions.

    The internal friction angle of the lunar soil was estimated from the geometry of rover tracks and astronaut footprints, assuming a known value for the bulk density of the surface material.
    These analyses provided qualitative confirmation of the soil’s mechanical properties as observed during previous missions.
    """)

    # --- Data and plot ---
    st.header("Lunar Regolith Density Variation with Depth")

    # Original data with depth ranges
    data = pd.DataFrame({
        "Testing Method": [
            "Drive tube", "Drive tube", "Drive tube", "Drive tube",
            "Drive tube", "Drive tube", "Drive tube", "Drive tube",
            "Drill stem", "Drill stem", "Drill stem", "Drill stem", "Drill stem", "Drill stem"
        ],
        "Depth range (cm)": [
            "0-22", "22-70", "0-33", "33-71",
            "0-16", "0-20", "20-71", "0-28",
            "0-305", "0-305", "0-305", "0-305", "0-305", "0-305"
        ],
        "Density (g/cm³)": [1.6, 1.73, 2.04, 2.29, 1.57, 1.67, 1.74, 1.77, 1.99, 1.8, 1.85, 1.84, 1.83, 1.74],
        "Porosity (%)": ["NA"] * 14,
        "Force Applied (N)": ["NA"] * 14
    })

    # --- Sidebar ---
    methods_selected = st.multiselect("Select Testing Method(s)", data["Testing Method"].unique(), default=data["Testing Method"].unique())
    value_to_plot = st.radio("Value to plot", ["Density (g/cm³)", "Porosity (%)", "Force Applied (N)"])
    filtered_data = data[data["Testing Method"].isin(methods_selected)].copy()

    # --- Prepare bars ---
    bars = []
    color_map = {method: px.colors.qualitative.Plotly[i % 10] for i, method in enumerate(filtered_data["Testing Method"].unique())}
    pattern_map = {"Drive tube":"","Drill stem":"/","Penetrometer":"\\","Footprint analysis":"x"}

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

        # Create a rectangle for each bar (x = value range, y = depth range)
        bars.append(go.Scatter(
            x=[val_start, val_end, val_end, val_start, val_start],
            y=[depth_start, depth_start, depth_end, depth_end, depth_start],
            fill="toself",
            fillcolor=color_map[row["Testing Method"]],
            line=dict(color='black'),
            opacity=0.5,
            name=row["Testing Method"],
            hoverinfo='text',
            hovertext=f"Method: {row['Testing Method']}<br>{value_to_plot}: {val_start}-{val_end}<br>Depth: {depth_start}-{depth_end} cm",
            showlegend=False
        ))

    fig = go.Figure(bars)

    # Add manual legend for methods
    for method, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color, line=dict(color='black'),
                        symbol='square'),
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
    