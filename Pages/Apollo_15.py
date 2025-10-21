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
        ]
    })

    # Sidebar filter for methods
    methods_selected = st.multiselect("Select Testing Method(s)", data["Testing Method"].unique(),
                                      default=data["Testing Method"].unique())
    filtered_data = data[data["Testing Method"].isin(methods_selected)].copy()

    # Convert depth and value ranges to numeric
    depth_val_data = []
    for _, row in filtered_data.iterrows():
        # Parse depth range
        try:
            depth_start, depth_end = map(float, row["Depth range (cm)"].split("-"))
        except:
            continue

        # Parse value range
        val_str = str(row["Density (g/cm³)"])
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

        depth_val_data.append({
            "Method": row["Testing Method"],
            "Depth Start": depth_start,
            "Depth End": depth_end,
            "Value Start": val_start,
            "Value End": val_end
        })

    depth_df = pd.DataFrame(depth_val_data)

    # Plot horizontal bars using shapes for ranges
    fig = go.Figure()
    color_map = {method: px.colors.qualitative.Plotly[i % 10] for i, method in enumerate(filtered_data["Testing Method"].unique())}

    # Small horizontal offset for overlapping bars
    offsets = {method: i*0.02 for i, method in enumerate(filtered_data["Testing Method"].unique())}

    for _, row in depth_df.iterrows():
        offset = offsets[row["Method"]]
        fig.add_shape(
            type="rect",
            x0=row["Value Start"] + offset,
            x1=row["Value End"] + offset,
            y0=row["Depth Start"],
            y1=row["Depth End"],
            line=dict(color="black"),
            fillcolor=color_map[row["Method"]],
            opacity=0.5,
            layer="below"
        )
        # Hover info as invisible scatter for tooltips
        fig.add_trace(go.Scatter(
            x=[(row["Value Start"]+row["Value End"])/2 + offset],
            y=[(row["Depth Start"]+row["Depth End"])/2],
            text=f"Method: {row['Method']}<br>Depth: {row['Depth Start']}-{row['Depth End']} cm<br>Value: {row['Value Start']}-{row['Value End']}",
            mode="markers",
            marker=dict(size=0.1, color=color_map[row["Method"]]),
            hoverinfo="text",
            showlegend=False
        ))

    # Add legend manually
    for method, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(color=color, size=10),
            name=method
        ))

    fig.update_layout(
        title="Density/Force vs Depth",
        xaxis_title="Density (g/cm³)",
        yaxis_title="Depth (cm)",
        yaxis=dict(autorange="reversed"),
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)