import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def show_mission():
    st.set_page_config(page_title="Apollo 16 Lunar Regolith Data", initial_sidebar_state="collapsed")

    st.title("Apollo 16 Lunar Regolith Data")

    st.write("""The Soil Mechanics Investigation during the Apollo 16 mission involved both in-situ measurements and observational analyses of the lunar surface. A penetrometer was used to obtain direct measurements of soil resistance, while additional data were gathered from visual observations of interactions between the soil and the rover wheels, drive tube insertions, and deep drill samples collected for return to Earth.

             The stability of the soil during drilling operations was also analyzed to estimate the cohesion of the regolith, assuming a known value for the internal friction angle. These combined observations provided further insight into the mechanical behavior and strength characteristics of the lunar surface material at the Apollo 16 landing site.""")

    # --- Data ---
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

    # --- Sidebar Filters ---
    methods_selected = st.multiselect(
        "Select Testing Method(s)", data["Testing Method"].unique(), default=data["Testing Method"].unique()
    )
    value_to_plot = st.radio("Value to plot", ["Density (g/cm³)", "Porosity (%)", "Force Applied (N)"])
    filtered_data = data[data["Testing Method"].isin(methods_selected)].copy()

    # --- Convert depth ranges and value ranges for plotting and table ---
    processed_data = []
    for _, row in filtered_data.iterrows():
        # Depth
        try:
            depth_start, depth_end = map(float, row["Depth range (cm)"].split("-"))
        except:
            continue

        # Value handling (supports ranges)
        val_str = str(row[value_to_plot])
        if val_str.upper() == "NA":
            val_start = val_end = None
        elif "-" in val_str:
            try:
                val_start, val_end = map(float, val_str.split("-"))
            except:
                val_start = val_end = None
        else:
            try:
                val_start = val_end = float(val_str)
            except:
                val_start = val_end = None

        processed_data.append({
            "Testing Method": row["Testing Method"],
            "Depth Start (cm)": depth_start,
            "Depth End (cm)": depth_end,
            f"{value_to_plot} Start": val_start,
            f"{value_to_plot} End": val_end
        })

    table_df = pd.DataFrame(processed_data)

    # --- Display table ---
    st.subheader(f"{value_to_plot} vs Depth Table")
    if not table_df.empty:
        st.dataframe(table_df)
    else:
        st.info("No data available for the selected filters.")

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
