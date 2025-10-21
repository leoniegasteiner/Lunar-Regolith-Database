import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page configuration ---
def show_mission():
    st.set_page_config(page_title="Apollo 11 Lunar Regolith Data", initial_sidebar_state="collapsed")

    st.title("Apollo 11 Lunar Regolith Data")

    st.header("The Apollo 11 Mission")
    st.write("""
    Specific scientific objectives of the Soil Mechanics Investigation at the Apollo 11 landing site included the following:
    to verify lunar soil models previously formulated from Earth-based observations, laboratory investigations, and data from lunar orbiting and unmanned landing missions.

    The Soil Mechanics Investigation pursued several engineering objectives: to obtain information on the interaction between the lunar module (LM) and the lunar surface during landing, to provide a basis for altering mission plans in response to unexpected surface conditions; to assess the effect of lunar soil properties on astronaut and surface vehicle mobility; and to gather at least qualitative information necessary for the deployment, installation, operation, and maintenance of scientific and engineering equipment for extended lunar exploration.

    Because no specific hardware could be added to the spacecraft for soil mechanics analysis, existing tools were repurposed from other experiments. These included astronaut and camera observations, spacecraft flight mechanics telemetry data, and various tools and poles inserted into the ground to observe its behavior.

    Core tube samples were brought back to Earth for laboratory analysis in the Lunar Regolith Laboratory. Testing of these samples with a penetrometer made it possible to determine a compressed bulk density and a range of cohesion values, providing the first direct mechanical characterization of lunar soil.
    """)

    # --- Data and plot ---
    st.header("Lunar Regolith Density Variation with Depth")

    # Data
    data = pd.DataFrame({
        "Testing Method": ["Penetrometer", "Penetrometer", "Penetrometer", "Core Tube"],
        "Depth (cm)": ["0-2", "0-2", "0-2", "0-10"],
        "Density (g/cm³)": [1.36, 1.77, 1.80, 1.66],
        "Porosity (%)": [None, None, None, 46.5],
        "Force Applied (N)": [1.82, 10.5, 54.5, None]
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
