import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        ],
        "Porosity (%)": [None, None, None, None, None, None, None, None, None, None, None, None, None],
        "Force Applied (N)": [None, None, None, None, None, None, None, None, None, None, None, None, None]
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