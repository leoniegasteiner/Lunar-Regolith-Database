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
        "Density (g/cm³)": ["NA", "NA", "1.75"],
        "Force Applied (N)": ["71-134", "134-223", "NA"]
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
