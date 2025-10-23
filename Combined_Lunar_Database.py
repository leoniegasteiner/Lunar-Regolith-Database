#Necessary imports
from email.quoprimime import quote
from altair import value
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import re
import base64
from io import BytesIO
from urllib.parse import quote
import importlib
import os

st.cache_data.clear()


#Lunar Data Loading 
@st.cache_data
def load_database_data():
    df = pd.read_csv(
    "Dataset_Regolith.csv",
    dtype=str,
    header=0,
    skip_blank_lines=False,
    )
    df.columns =  ["Mission", "Location", "Terrain","Year","Type of mission","Test", "Test location", "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Static bearing capacity (kPa)", "Source","Year of publication", "DOI / URL"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

# Numerical data for plotting loading
@st.cache_data
def load_plot_data():
    df = pd.read_csv("Dataset_Regolith_plots.csv")
    df.columns =  [
        "Mission", "Location", "Terrain","Year","Type of mission","Test", "Test location",
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Static bearing capacity (kPa)", "Source","Year of publication", "DOI / URL"
    ]
    numeric_cols = ["Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Static bearing capacity (kPa)"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

lunar_db_df = load_database_data()
lunar_plot_df = load_plot_data()


#Simulants Data Loading
@st.cache_data
def load_Simulants_data():
    df = pd.read_csv(
    "Dataset_Simulants.csv",
    dtype=str,
    header=0,
    skip_blank_lines=False,
    )
    df.columns =  ["Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Source","Date of publication","DOI / URL"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

# Numerical data for plotting loading 
@st.cache_data
def load_Simulant_plot_data():
    df = pd.read_csv("Dataset_Simulants_plots.csv")
    df.columns =  [
        "Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Source","Date of publication","DOI / URL"
    ]
    numeric_cols = ["Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
simulant_db_df = load_Simulants_data()
simulant_plot_df = load_Simulant_plot_data()

#All data loading
@st.cache_data
def load_database_data():
    df = pd.read_csv(
    "Dataset_All.csv",
    dtype=str,
    header=0,
    skip_blank_lines=False,
    )
    df.columns =  ["Mission/Simulant", "Developer", "Agency", "Moon Location/Country", "Year", "Terrain type", "Type of mission", "Test", "Test location", "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Static bearing capacity (kPa)", "Original source", "DOI / URL"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df


# Sidebar to choose database (Lunar mission or Simulants)
db_choice = st.sidebar.radio(
    "Select Database:",
    ["Moon Mission Database", "Lunar Regolith Simulants Database", "All Data", "Detailed Mission Pages"]
)

# --------------------------- Lunar Mission Database Section ---------------------------
if db_choice == "Moon Mission Database":

    st.title("Lunar Regolith Database")

    # Mission categorization function
    def categorize_mission(mission_name):
        if pd.isna(mission_name):
            return "Other"
        name = mission_name.lower()
        if "apollo" in name:
            return "Apollo"
        elif "luna" in name:
            return "Luna"
        elif "surveyor" in name:
            return "Surveyor"
        elif "chang'e" in name:
            return "Chang'e"
        elif "chandrayaan" in name: 
            return "Chandrayaan"
        else:
            return "Other"
        
    def extract_range(value):
        """Extracts min and max numeric values from strings"""
        if pd.isna(value):
            return (np.nan, np.nan)
        if isinstance(value, (int, float)):
            return (float(value), float(value))
        match = re.findall(r"[-+]?\d*\.?\d+", str(value))
        if len(match) == 0:
            return (np.nan, np.nan)
        elif len(match) == 1:
            val = float(match[0])
            return (val, val)
        else:
            return (float(match[0]), float(match[-1]))  # take first and last

    # --- Columns that may contain ranges ---
    range_columns = [
        "Bulk density (g/cm^3)",
        "Angle of internal friction (degree)",
        "Cohesion (kPa)",
        "Static bearing capacity (kPa)",
    ]

    # --- Apply extraction and create numeric columns ---
    for col in range_columns:
        if col in lunar_db_df.columns:
            lunar_db_df[[f"{col}_min", f"{col}_max"]] = lunar_db_df[col].apply(
                lambda x: pd.Series(extract_range(x))
            )

    lunar_db_df["Mission Group"] = lunar_db_df["Mission"].apply(categorize_mission)

    # Sidebar Filters
    with st.sidebar:
        st.header("Filter Regolith Data")
        #original filters 
        soil_group_filter = st.multiselect("Select Terrain type", ["Mare", "Highland"])
        test_filter = st.multiselect("Select Test Type", lunar_db_df["Test"].dropna().unique())
        # --- Text / Categorical Filters ---
        mission_type_filter = st.multiselect(
            "Select type of mission:",
            options=sorted(lunar_db_df["Type of mission"].dropna().unique())
        )

        mission_group_filter = st.multiselect(
            "Select Mission Group", 
            options=["Apollo", "Luna", "Surveyor", "Chang'e", "Chandrayaan", "Other"]
        )

        # --- Numeric Range Filters ---
        st.markdown("### Publication Year")
        if "Date of publication" in lunar_db_df.columns and lunar_db_df["Date of publication"].notna().any():
            year_min, year_max = int(lunar_db_df["Date of publication"].min()), int(lunar_db_df["Date of publication"].max())
            year_range = st.slider(
                "Select Year of publication Range",
                min_value=year_min,
                max_value=year_max,
                value=(year_min, year_max)
            )
        else:
            year_range = None


        st.markdown("### Density (g/cm³)")
        if "Bulk density (g/cm^3)_min" in lunar_db_df.columns:
            dens_min = float(lunar_db_df["Bulk density (g/cm^3)_min"].min(skipna=True))
            dens_max = float(lunar_db_df["Bulk density (g/cm^3)_max"].max(skipna=True))
            density_range = st.slider(
                "Select Density Range",
                min_value=round(dens_min, 2),
                max_value=round(dens_max, 2),
                value=(round(dens_min, 2), round(dens_max, 2))
            )
        else:
            density_range = None

        st.markdown("### Cohesion (kPa)")
        if "Cohesion (kPa)_min" in lunar_db_df.columns:
            coh_min = float(lunar_db_df["Cohesion (kPa)_min"].min(skipna=True))
            coh_max = float(lunar_db_df["Cohesion (kPa)_max"].max(skipna=True))
            cohesion_range = st.slider(
                "Select Cohesion Range",
                min_value=round(coh_min, 1),
                max_value=round(coh_max, 1),
                value=(round(coh_min, 1), round(coh_max, 1))
            )
        else:
            cohesion_range = None
        st.markdown("### Angle of Internal Friction (°)")
        if "Angle of internal friction (degree)_min" in lunar_db_df.columns:
            ang_min = float(lunar_db_df["Angle of internal friction (degree)_min"].min(skipna=True))
            ang_max = float(lunar_db_df["Angle of internal friction (degree)_max"].max(skipna=True))
            angle_range = st.slider(
                "Select Angle Range",
                min_value=round(ang_min, 1),
                max_value=round(ang_max, 1),
                value=(round(ang_min, 1), round(ang_max, 1))
            )
        else:
            angle_range = None
        st.markdown("### Static Bearing Capacity (kPa)")
        if "Static bearing capacity (kPa)_min" in lunar_db_df.columns:
            sbc_min = float(lunar_db_df["Static bearing capacity (kPa)_min"].min(skipna=True))
            sbc_max = float(lunar_db_df["Static bearing capacity (kPa)_max"].max(skipna=True))
            sbc_range = st.slider(
               "Select Static Bearing Capacity Range",
               min_value=round(sbc_min, 1),
               max_value=round(sbc_max, 1),
               value=(round(sbc_min, 1), round(sbc_max, 1))
           )
        else:
            sbc_range = None

        # --- Column Selection ---
        st.divider()
        st.header("Display Options")
        all_columns = lunar_db_df.columns.tolist()
        default_columns = ["Mission", "Year", "Test", "Bulk density (g/cm^3)", "Cohesion (kPa)"]
        selected_columns = st.multiselect(
            "Select columns to display:",
            options=all_columns,
            default=[col for col in default_columns if col in all_columns]
        )


    # --- Apply Filters ---
    filtered_db_df = lunar_db_df.copy()
    
    # Terrain type filter
    if soil_group_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Terrain"].isin(soil_group_filter)]
    
    # Test type filter
    if test_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Test"].isin(test_filter)]
    
    # Mission group filter (use Mission Group, not Mission)
    if mission_group_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Mission Group"].isin(mission_group_filter)]
    
    # Mission type filter
    if mission_type_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Type of mission"].isin(mission_type_filter)]
    
    # Year of publication filter (only if slider active)
    if year_range:
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Year of publication"] >= year_range[0]) &
            (filtered_db_df["Year of publication"] <= year_range[1])
        ]
    
    # --- Numeric filters (keep NaN rows visible) ---
    def filter_numeric_range(df, col_min, col_max, min_val, max_val):
        """Filter keeping NaNs visible."""
        return df[
            ((df[col_max].ge(min_val)) | (df[col_max].isna())) &
            ((df[col_min].le(max_val)) | (df[col_min].isna()))
        ]
    
    if density_range:
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "Bulk density (g/cm^3)_min", "Bulk density (g/cm^3)_max",
            density_range[0], density_range[1]
        )
    
    if cohesion_range:
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "Cohesion (kPa)_min", "Cohesion (kPa)_max",
            cohesion_range[0], cohesion_range[1]
        )
    
    if angle_range:
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "Angle of internal friction (degree)_min", "Angle of internal friction (degree)_max",
            angle_range[0], angle_range[1]
        )
    
    if sbc_range:
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "Static bearing capacity (kPa)_min", "Static bearing capacity (kPa)_max",
            sbc_range[0], sbc_range[1]
        )
    
    # --- Display filtered table ---
    st.subheader("Database Table")
    if selected_columns:
        st.dataframe(filtered_db_df[selected_columns])
    else:
        st.info("No columns selected. Please select at least one column to display.")
    
    st.markdown(
        "<p style='font-size:12px; color:gray;'>Note: Values are for the top 10 cm of lunar soil, see missions details for more depths.<br>* Indicates values estimated for the measurements.</p>",
        unsafe_allow_html=True
    )



    # Plotting Section & Display
    st.subheader("Plot Numerical Data")

    x_axis = st.selectbox("X-axis (categorical)", options=[
        "Mission", "Location", "Terrain", "Test", "Type of mission", 
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Static bearing capacity (kPa)"
    ])
    y_axis = st.selectbox("Y-axis (numeric)", options=[
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Static bearing capacity (kPa)"
    ])

    lunar_plot_df["Mission Group"] = lunar_plot_df["Mission"].apply(categorize_mission)

    # Filters application 
    filtered_plot_df = lunar_plot_df.copy()
    if mission_group_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Mission Group"].isin(mission_group_filter)]
    if test_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Test"].isin(test_filter)]
    if soil_group_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Terrain"].isin(soil_group_filter)]

    # Plotting markers
    marker_shapes = {
        "Apollo": "circle",
        "Luna": "square",
        "Surveyor": "triangle-up",
        "Chang'e": "diamond",
        "Chandrayaan": "cross"
    }
    color_map = {
        "Apollo": "#0b96d6",
        "Luna": "#d45087",
        "Surveyor": "#ffa600",
        "Chang'e": "#72CF6D",
        "Chandrayaan": "#8e44ad",
    }

    compare_simulants = st.checkbox("Compare with lunar regolith simulants")

    filtered_plot_df = filtered_plot_df.dropna(subset=[x_axis, y_axis])
    if not filtered_plot_df.empty:
        fig = px.scatter(
            filtered_plot_df,
            x=x_axis,
            y=y_axis,
            color="Mission Group",
            symbol="Mission Group",
            color_discrete_map=color_map,
            symbol_map=marker_shapes,
            hover_data=["Mission", x_axis, y_axis],
            title=f"{y_axis} vs {x_axis}",
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        fig.update_layout(
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
            title=dict(
                x=0,
                xanchor='left',
                font=dict(size=20)
            ),
            legend_title_text="Mission Group",
            width=800,
            height=500,
        )

        # Add simulants if selected
        if compare_simulants:
            if x_axis in simulant_plot_df.columns and y_axis in simulant_plot_df.columns:
                hover_texts = [
                    f"Simulant: {row['Simulant']}<br>{x_axis}: {row[x_axis]}<br>{y_axis}: {row[y_axis]}"
                    for _, row in simulant_plot_df.iterrows()
                ]
                fig.add_scatter(
                    x=simulant_plot_df[x_axis],
                    y=simulant_plot_df[y_axis],
                    mode='markers',
                    name='Lunar Simulants',
                    marker=dict(symbol='diamond', size=10, color='#ff00ff', line=dict(width=1, color='black')),
                    hovertext=hover_texts,
                    hoverinfo='text'
                )
            else:
                st.warning(f"'{x_axis}' or '{y_axis}' not found in simulant dataset.")

        # Updated config dictionary
        config = {
            "displayModeBar": False,  # hides the toolbar
            "scrollZoom": True
        }

        st.plotly_chart(fig, use_container_width=True, config=config)
    else:
        st.info("No data available for the selected plot.")


    # Moon Map
    def parse_location(loc_str):
        if pd.isna(loc_str):
            return None, None
        # Match something like: 3.01239S 23.42157W
        match = re.match(r"([0-9.+-]+)([NS])\s+([0-9.+-]+)([EW])", loc_str.strip())
        if not match:
            return None, None
        lat_val, lat_dir, lon_val, lon_dir = match.groups()
        lat = float(lat_val) * (1 if lat_dir.upper() == "N" else -1)
        lon = float(lon_val) * (1 if lon_dir.upper() == "E" else -1)
        return lat, lon

    lunar_plot_df["Latitude"], lunar_plot_df["Longitude"] = zip(*lunar_plot_df["Location"].apply(parse_location))

    # Load Moon map image
    def pil_to_base64_uri(pil_img):
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        base64_str = base64.b64encode(img_bytes).decode()
        return "data:image/png;base64," + base64_str


    moon_img = Image.open("moon_map.jpg")

    if moon_img.mode != 'RGB':
        moon_img = moon_img.convert('RGB')

    moon_img_uri = pil_to_base64_uri(moon_img)

    fig = go.Figure()

    for group in lunar_plot_df["Mission Group"].unique():
        df_group = lunar_plot_df[lunar_plot_df["Mission Group"] == group]
        hover_text = df_group.apply(
            lambda row: f"Mission: {row['Mission']}<br>Longitude: {row['Longitude']}°<br>Latitude: {row['Latitude']}°", 
            axis=1
        )
        fig.add_trace(go.Scatter(
            x=df_group["Longitude"],
            y=df_group["Latitude"],
            mode="markers",
            marker=dict(
                size=10,
                color=color_map.get(group, "black"),
                symbol=marker_shapes.get(group, "circle"),
                opacity=0.8,
                line=dict(width=0)
            ),
            text=hover_text,
            hoverinfo="text",
            name=group   
        ))

    fig.add_layout_image(
        dict(
            source=moon_img_uri,
            xref="x",
            yref="y",
            x=-180,
            y=90,
            sizex=360,
            sizey=180,
            sizing="stretch",
            opacity=1,
            layer="below"
        )
    )

    fig.update_layout(
        title=dict(
            text="Mission Location Representation on the Moon",
            x=0,
            xanchor='left',
            y=0.8,
            yanchor='top',
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Longitude (°)",
            range=[-180, 180],
            constrain='domain',
            scaleratio=1,
            scaleanchor="y",
            fixedrange=True,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(
                text="Latitude (°)",
                standoff=20 
            ),
            range=[-90, 90],
            constrain='domain',
            fixedrange=True,
            showgrid=False,
            zeroline=False,
        ),
        margin=dict(l=80, r=20, t=20, b=40), 
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            title="Mission Group",
            y=0.8, 
            yanchor="top", 
            x=1,   
            xanchor="left",
        ),
        hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
        width=800,
        height=600
    )

    fig.update_xaxes(automargin=False)
    fig.update_yaxes(automargin=False)

    config_map = {
    "displayModeBar": False,
    "scrollZoom": True
    }
    st.plotly_chart(fig, use_container_width=True, height=800, config=config_map)


# --------------------------- Lunar Simulants Database Section ---------------------------

elif db_choice == "Lunar Regolith Simulants Database":

    st.title("Lunar Regolith Simulants Database")
    simulant_db_df.columns = simulant_db_df.columns.str.strip()
    numeric_cols = ["Year","Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Date of publication"]
    for col in numeric_cols:
        if col in simulant_db_df.columns:
            simulant_db_df[col] = pd.to_numeric(simulant_db_df[col], errors="coerce")

    # Soil categorization function
    def categorize_soil(soil_name):
        if pd.isna(soil_name):
            return "Other"
        name = soil_name.lower()
        if "mare" in name:
            return "Mare"
        elif "highland" in name:
            return "Highland"
        else:
            return "Other"

    simulant_db_df["Soil Group"] = simulant_db_df["Type of simulant"].apply(categorize_soil)


    with st.sidebar:
            st.header("Filter Simulant Data")
            #original filters 
            soil_group_filter = st.multiselect("Select Type of Simulant", ["Mare", "Highland"])
            test_filter = st.multiselect("Select Test Type", simulant_db_df["Test"].dropna().unique())
            agency_filter = st.multiselect("Select Agency", ["NASA", "ESA", "JAXA", "KASA", "ISRO", "CNSA", "GISTDA"])
            # --- Text / Categorical Filters ---
            developer_filter = st.multiselect(
                "Select Developer(s):",
                options=sorted(simulant_db_df["Developer"].dropna().unique())
            )

            #country_filter = st.multiselect(
            #    "Select Country:",
            #    options=sorted(simulant_db_df["Moon Location/Country"].dropna().unique())
            #)         )

            # --- Numeric Range Filters ---
            st.markdown("### Publication Year")
            if "Date of publication" in simulant_db_df.columns and simulant_db_df["Date of publication"].notna().any():
                year_min, year_max = int(simulant_db_df["Date of publication"].min()), int(simulant_db_df["Date of publication"].max())
                year_range = st.slider(
                    "Select Year of publication Range",
                    min_value=year_min,
                    max_value=year_max,
                    value=(year_min, year_max)
                )
            else:
                year_range = None

            st.markdown("### Density (g/cm³)")
            if "Bulk density (g/cm^3)" in simulant_db_df.columns:
                dens_min, dens_max = float(simulant_db_df["Bulk density (g/cm^3)"].min()), float(simulant_db_df["Bulk density (g/cm^3)"].max())
                density_range = st.slider(
                    "Select Density Range",
                    min_value=round(dens_min, 2),
                    max_value=round(dens_max, 2),
                    value=(round(dens_min, 2), round(dens_max, 2))
                )
            else:
                density_range = None

            st.markdown("### Cohesion (kPa)")
            if "Cohesion (kPa)" in simulant_db_df.columns:
                coh_min, coh_max = float(simulant_db_df["Cohesion (kPa)"].min()), float(simulant_db_df["Cohesion (kPa)"].max())
                cohesion_range = st.slider(
                    "Select Cohesion Range",
                    min_value=round(coh_min, 1),
                    max_value=round(coh_max, 1),
                    value=(round(coh_min, 1), round(coh_max, 1))
                )
            else:
                cohesion_range = None

            st.markdown("### Angle of Internal Friction (°)")
            if "Angle of internal friction (degree)" in simulant_db_df.columns:
                ang_min, ang_max = float(simulant_db_df["Angle of internal friction (degree)"].min()), float(simulant_db_df["Angle of internal friction (degree)"].max())
                angle_range = st.slider(
                    "Select Angle Range",
                    min_value=round(ang_min, 1),
                    max_value=round(ang_max, 1),
                    value=(round(ang_min, 1), round(ang_max, 1))
                )
            else:
                angle_range = None

            #st.markdown("### Static Bearing Capacity (kPa)")
            #if "Static bearing capacity (kPa)" in simulant_df.columns:
            #    sbc_min, sbc_max = float(simulant_df["Static bearing capacity (kPa)"].min()), float(simulant_df["Static bearing capacity (kPa)"].max())
            #    sbc_range = st.slider(
            #        "Select Static Bearing Capacity Range",
            #        min_value=round(sbc_min, 1),
            #        max_value=round(sbc_max, 1),
            #        value=(round(sbc_min, 1), round(sbc_max, 1))
            #    )
            #else:
            #    sbc_range = None

            st.markdown("### Normal Force (N) [To be implemented]")
            # Placeholder for when you add this column later
            # normal_force_range = st.slider("Select Normal Force Range", min_value=0, max_value=1000, value=(0, 1000))
            normal_force_range = None



            # --- Column Selection ---
            st.divider()
            st.header("Display Options")
            all_columns = simulant_db_df.columns.tolist()
            default_columns = ["Simulant", "Year", "Test", "Bulk density (g/cm^3)", "Cohesion (kPa)"]
            selected_columns = st.multiselect(
                "Select columns to display:",
                options=all_columns,
                default=[col for col in default_columns if col in all_columns]
            )


    filtered_db_df = simulant_db_df.copy()
    if soil_group_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Soil Group"].isin(soil_group_filter)]
    if test_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Test"].isin(test_filter)]
    if agency_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Agency"].isin(agency_filter)]
    if developer_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Developer"].isin(developer_filter)]
    if year_range:
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Date of publication"] >= year_range[0]) & (filtered_db_df["Date of publication"] <= year_range[1])
        ]
    if density_range:
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Bulk density (g/cm^3)"] >= density_range[0]) &
            (filtered_db_df["Bulk density (g/cm^3)"] <= density_range[1])
        ]
    if cohesion_range:
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Cohesion (kPa)"] >= cohesion_range[0]) &
            (filtered_db_df["Cohesion (kPa)"] <= cohesion_range[1])
        ]
    if angle_range:
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Angle of internal friction (degree)"] >= angle_range[0]) &
            (filtered_db_df["Angle of internal friction (degree)"] <= angle_range[1])
        ]
    #if sbc_range:
    #    filtered_db_df = filtered_db_df[
    #        (filtered_db_df["Static bearing capacity (kPa)"] >= sbc_range[0]) &
    #        (filtered_db_df["Static bearing capacity (kPa)"] <= sbc_range[1])
    #    ]
    # Table display
    st.subheader("Database Table")
    if selected_columns:  # avoid empty selection
        st.dataframe(filtered_db_df[selected_columns])
    else:
        st.info("No columns selected. Please select at least one column to display.")

    # Plotting Section & Display
    st.subheader("Plot Numerical Data")
    x_axis = st.selectbox("X-axis (categorical)", [
        "Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)"
    ])
    y_axis = st.selectbox("Y-axis (numeric)", [
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)"
    ])

    
    filtered_plot_df = filtered_db_df.dropna(subset=[x_axis, y_axis])

    if not filtered_plot_df.empty:
        fig = px.scatter(
            filtered_plot_df,
            x=x_axis,
            y=y_axis,
            color="Soil Group",
            symbol="Soil Group",
            color_discrete_map={"Mare": "#4dbaed", "Highland": "#d45087", "Other": "#84ebbb"},
            symbol_map={"Mare": "circle", "Highland": "square"},
            hover_data=["Simulant", x_axis, y_axis],
            title=f"{y_axis} vs {x_axis}",
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))

        # Config for Plotly
        config_simulant = {"displayModeBar": False, "scrollZoom": True}

        st.plotly_chart(fig, use_container_width=True, config=config_simulant)
    else:
        st.info("No data available for the selected plot.")



# --------------------------- All Data Section ---------------------------
elif db_choice == "All Data":
    st.title("Combined Lunar Regolith Database")

    # --- Detect correct mission column ---
    mission_col_candidates = ["Mission/Simulant", "Mission", "Mission Name"]
    mission_col = next((col for col in mission_col_candidates if col in lunar_db_df.columns), None)

    if mission_col is None:
        st.error("❌ Could not find a mission column. Expected one of: 'Mission/Simulant', 'Mission', or 'Mission Name'.")
    else:
        # --- Categorize missions ---
        def categorize_mission(mission_name):
            if pd.isna(mission_name):
                return "Other"
            name = mission_name.lower()
            if "apollo" in name:
                return "Apollo"
            elif "luna" in name:
                return "Luna"
            elif "surveyor" in name:
                return "Surveyor"
            elif "chang'e" in name or "change" in name:
                return "Chang'e"
            elif "chandrayaan" in name:
                return "Chandrayaan"
            else:
                return "Simulant"

        lunar_db_df["Mission Group"] = lunar_db_df[mission_col].apply(categorize_mission)

        # --- Sidebar filters ---
        with st.sidebar:
            st.header("🔍 Filter Database")

            mission_group_filter = st.multiselect(
                "Select Mission Group", 
                options=sorted(lunar_db_df["Mission Group"].dropna().unique())
            )

            test_filter = st.multiselect(
                "Select Test Type", 
                options=sorted(lunar_db_df["Test"].dropna().unique())
            )

            terrain_filter = st.multiselect(
                "Select Terrain Type",
                options=sorted(lunar_db_df["Terrain type"].dropna().unique())
            )

            year_filter = st.slider(
                "Select Year Range",
                int(lunar_db_df["Year"].min()),
                int(lunar_db_df["Year"].max()),
                (int(lunar_db_df["Year"].min()), int(lunar_db_df["Year"].max()))
            )

        # --- Apply filters ---
        filtered_db_df = lunar_db_df.copy()

        if mission_group_filter:
            filtered_db_df = filtered_db_df[filtered_db_df["Mission Group"].isin(mission_group_filter)]
        if test_filter:
            filtered_db_df = filtered_db_df[filtered_db_df["Test"].isin(test_filter)]
        if terrain_filter:
            filtered_db_df = filtered_db_df[filtered_db_df["Terrain type"].isin(terrain_filter)]
        if year_filter:
            filtered_db_df = filtered_db_df[
                (filtered_db_df["Year"] >= year_filter[0]) & 
                (filtered_db_df["Year"] <= year_filter[1])
            ]

        # --- Display table ---
        st.subheader("📊 Filtered Lunar Regolith Data")
        st.dataframe(filtered_db_df, use_container_width=True)


# ------------------Mission Details Section ------------------
elif db_choice == "Detailed Mission Pages":
    st.title("Detailed Lunar Mission Pages")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MISSION_DIR = os.path.join(BASE_DIR, "Pages")

    if not os.path.exists(MISSION_DIR):
        st.error(f"❌ Could not find mission directory: {MISSION_DIR}")
    else:
        # --- List all mission scripts ---
        available_missions = {}
        for filename in os.listdir(MISSION_DIR):
            if filename.endswith(".py"):
                mission_name = filename[:-3].replace("_", " ").title()
                available_missions[mission_name] = os.path.join(MISSION_DIR, filename)

        # --- Sidebar selection ---
        st.sidebar.header("Mission Selection")
        mission_choice = st.sidebar.selectbox(
            "Select a mission to view details:",
            options=[""] + sorted(list(available_missions.keys())),  # empty default (none selected)
            format_func=lambda x: "Select a mission" if x == "" else x
        )

        # --- Load and display selected mission page ---
        if mission_choice:
            st.divider()
            st.subheader(f"📄 Detailed Data for {mission_choice}")

            mission_file = available_missions[mission_choice]
            spec = importlib.util.spec_from_file_location("mission_module", mission_file)
            mission_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mission_module)

            if hasattr(mission_module, "show_mission"):
                mission_module.show_mission()  # Run mission page script
            else:
                st.warning("No show_mission() function found in this mission script.")
        else:
            st.info("Select a mission from the sidebar to display its detailed page.")

# ------------------- Footer --------------------
import requests
import datetime


def get_last_commit_date(repo="leoniegasteiner/Lunar-Regolith-Database", branch="main"):
    try:
        token = st.secrets.get("GITHUB_TOKEN", None)
        headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            headers["Authorization"] = f"token {token}"

        url = f"https://api.github.com/repos/{repo}/commits/{branch}"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        data = resp.json()
        commit_iso = data["commit"]["committer"]["date"]
        dt = datetime.datetime.fromisoformat(commit_iso.replace("Z", "+00:00"))
        return dt.strftime("%d %B %Y")

    except Exception as e:
        st.write("⚠️ Could not fetch last commit date:", e)
        return "Unknown"

last_updated = get_last_commit_date()

st.markdown(
    f"<hr><p style='font-size:11px; color:gray; text-align:center;'>© 2025 Lunar Regolith Database <br> Contact us at gasteinerleonie@gmail.com <br> Last updated: {last_updated}</p>",
    unsafe_allow_html=True
)

