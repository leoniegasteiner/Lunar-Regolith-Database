import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def show_mission():
    st.set_page_config(page_title="Apollo 16 Lunar Regolith Data", initial_sidebar_state="collapsed")

    st.title("Apollo 16 Lunar Regolith Data")

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

    # --- Sidebar ---
    methods_selected = st.multiselect("Select Testing Method(s)", data["Testing Method"].unique(), default=data["Testing Method"].unique())
    value_to_plot = st.radio("Value to plot", ["Density (g/cm³)", "Porosity (%)", "Force Applied (N)"])

    filtered_data = data[data["Testing Method"].isin(methods_selected)].copy()

    # --- Convert depth ranges and handle numeric/range values ---
    depth_data = []
    for _, row in filtered_data.iterrows():
        try:
            depth_start, depth_end = map(float, row["Depth range (cm)"].split("-"))
        except:
            continue

        val_str = str(row[value_to_plot])
        # Skip if value is not numeric or a range
        if val_str.upper() == "NA":
            continue
        if "-" in val_str:
            try:
                val_start, val_end = map(float, val_str.split("-"))
            except:
                continue
        else:
            try:
                val_start = val_end = float(val_str)
            except:
                continue

        depth_data.append({
            "Method": row["Testing Method"],
            "Depth Start": depth_start,
            "Depth End": depth_end,
            "Value Start": val_start,
            "Value End": val_end
        })

    depth_df = pd.DataFrame(depth_data)

    if depth_df.empty:
        st.info(f"No valid {value_to_plot} data to plot for selected methods.")
        return

    # --- Plot ---
    fig = go.Figure()
    color_map = {method: px.colors.qualitative.Plotly[i % 10] for i, method in enumerate(filtered_data["Testing Method"].unique())}
    pattern_map = {
        "Drive tube": "", 
        "Drill stem": "/", 
        "Penetrometer": "\\", 
        "Footprint analysis": "x"
    }

    method_offsets = {method: i*0.05 for i, method in enumerate(filtered_data["Testing Method"].unique())}

    for _, row in depth_df.iterrows():
        offset = method_offsets[row["Method"]]
        fig.add_shape(
            type="rect",
            x0=row["Value Start"] + offset,
            x1=row["Value End"] + offset,
            y0=row["Depth Start"],
            y1=row["Depth End"],
            line=dict(color="black"),
            fillcolor=color_map[row["Method"]],
            opacity=0.5
        )
        # Invisible scatter for hover
        fig.add_trace(go.Scatter(
            x=[(row["Value Start"] + row["Value End"])/2 + offset],
            y=[(row["Depth Start"] + row["Depth End"])/2],
            text=f"Method: {row['Method']}<br>{value_to_plot}: {row['Value Start']}-{row['Value End']}<br>Depth: {row['Depth Start']}–{row['Depth End']} cm",
            mode="markers",
            marker=dict(size=0.1, color=color_map[row["Method"]]),
            hoverinfo="text",
            showlegend=False
        ))

    # Legend
    for method, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(color=color, size=10),
            name=method
        ))

    fig.update_layout(
        title=f"{value_to_plot} vs Depth",
        xaxis_title=value_to_plot,
        yaxis_title="Depth (cm)",
        yaxis=dict(autorange="reversed"),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
