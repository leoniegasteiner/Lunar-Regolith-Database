import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def show_mission():
    st.set_page_config(page_title="Apollo 16 Lunar Regolith Data", initial_sidebar_state="collapsed")

    st.title("Apollo 16 Lunar Regolith Data")

    st.header("The Apollo 16 Mission")
    st.write("""
    The Soil Mechanics Investigation during the Apollo 16 mission involved both in-situ measurements and observational analyses of the lunar surface.
    A penetrometer was used to obtain direct measurements of soil resistance, while additional data were gathered from visual observations of interactions between the soil and the rover wheels, drive tube insertions, and deep drill samples collected for return to Earth.
    """)

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
    methods_selected = st.multiselect("Select Testing Method(s)", data["Testing Method"].unique(), default=data["Testing Method"].unique())
    value_to_plot = st.radio("Value to plot", ["Density (g/cm³)", "Porosity (%)", "Force Applied (N)"])

    filtered_data = data[data["Testing Method"].isin(methods_selected)].copy()

    # --- Convert depth ranges into numeric start/end points ---
    depth_data = []
    for _, row in filtered_data.iterrows():
        try:
            start, end = map(float, row["Depth range (cm)"].split("-"))
            depth_data.append({"Start": start, "End": end, "Value": row[value_to_plot], "Method": row["Testing Method"]})
        except Exception:
            pass

    depth_df = pd.DataFrame(depth_data)

    # --- Plot vertical bars for depth ranges ---
    fig = go.Figure()
    color_map = {method: px.colors.qualitative.Plotly[i % 10] for i, method in enumerate(filtered_data["Testing Method"].unique())}
    pattern_map = {
        "Drive tube": "", 
        "Drill stem": "/", 
        "Penetrometer": "\\", 
        "Footprint analysis": "x"
    }

    # offset bars horizontally to avoid full overlap
    method_offsets = {method: i*0.15 for i, method in enumerate(filtered_data["Testing Method"].unique())}

    for _, row in depth_df.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Value"] + method_offsets[row["Method"]]],  # small horizontal offset
            y=[row["End"] - row["Start"]],
            base=row["Start"],
            orientation='v',
            width=0.025, 
            name=row["Method"],
            marker=dict(
                color=color_map[row["Method"]],
                line=dict(color='black', width=1),
                pattern=dict(shape=pattern_map.get(row["Method"], ""), fillmode="overlay")
            ),
            opacity=0.6,
            hovertext=f"Method: {row['Method']}<br>{value_to_plot}: {row['Value']}<br>Depth: {row['Start']}–{row['End']} cm",
            hoverinfo="text",
            showlegend=False  # legends can be added separately
        ))

    # add manual legend for methods
    for method, color in color_map.items():
        fig.add_trace(go.Bar(
            x=[None], y=[None],
            name=method,
            marker=dict(color=color, line=dict(color='black', width=1),
                        pattern=dict(shape=pattern_map.get(method, ""), fillmode="overlay")),
            showlegend=True
        ))

    fig.update_layout(
        title=f"{value_to_plot} vs Depth",
        xaxis_title=value_to_plot,
        yaxis_title="Depth (cm)",
        yaxis=dict(autorange="reversed"),  # deeper = downward
        barmode='overlay',
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


