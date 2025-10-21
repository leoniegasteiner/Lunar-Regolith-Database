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