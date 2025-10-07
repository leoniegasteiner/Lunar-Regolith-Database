import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image


# Load database data for table display
@st.cache_data
def load_database_data():
    df = pd.read_csv(
    "Dataset for Rheology of Lunar Regolith - Regolith cleanedup (2).csv",
    dtype=str,
    header=0,
    skip_blank_lines=False
    )
    df.columns =  [
        "Mission", "Location", "Area","Year","Type of mission","Test", "Test location",
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Static bearing capacity (kPa)", "Original source", "Link"
    ]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

# Load numerical data for plotting
@st.cache_data
def load_plot_data():
    df = pd.read_csv("Dataset for Rheology of Lunar Regolith - regolith plots (1).csv")
    df.columns =  [
        "Mission", "Location", "Year","Type of mission","Test", "Test location",
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Static bearing capacity (kPa)", "Original source", "Link"
    ]
    numeric_cols = ["Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Static bearing capacity (kPa)"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

db_df = load_database_data()
plot_df = load_plot_data()

st.title("Lunar Regolith Database")

# separate the different types of missions
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
    else:
        return "Other"

db_df["Mission Group"] = db_df["Mission"].apply(categorize_mission)



# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filter Database")
    
    mission_group_filter = st.multiselect(
        "Select Mission Group", 
        options=["Apollo", "Luna", "Surveyor", "Other"]
    )
    
    test_filter = st.multiselect(
        "Select Test Type", 
        options=db_df["Test"].dropna().unique()
    )
    area_filter = st.multiselect(
        "Select Area",
        options=["Mare", "Highland"]
    )


filtered_db_df = db_df.copy()
if mission_group_filter:
    filtered_db_df = filtered_db_df[filtered_db_df["Mission Group"].isin(mission_group_filter)]
if test_filter:
    filtered_db_df = filtered_db_df[filtered_db_df["Test"].isin(test_filter)]
if area_filter:
    filtered_db_df = filtered_db_df[filtered_db_df["Area"].isin(area_filter)]


# --- Display Database Table ---
st.subheader("Database Table")
st.dataframe(filtered_db_df)



# --- Plotting ---
st.subheader("Plot Numerical Data")


x_axis = st.selectbox("X-axis (categorical)", options=["Mission", "Location", "Test", "Type of mission", "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Static bearing capacity (kPa)"])
y_axis = st.selectbox("Y-axis (numeric)", options=[
    "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
    "Cohesion (kPa)", "Static bearing capacity (kPa)"
])

plot_df["Mission Group"] = plot_df["Mission"].apply(categorize_mission)

#Marker shapes and colors for mission groups 
marker_shapes = {
    "Apollo": "circle",
    "Luna": "square",
    "Surveyor": "triangle-up",
    "Other": "diamond"
}

color_map = {
    "Apollo": "#003f5c",   # deep blue
    "Luna": "#d45087",     # crimson red
    "Surveyor": "#ffa600", # bright orange
    "Other": "#7a5195"     # purple
}


plot_df = plot_df.dropna(subset=[x_axis, y_axis])
if not plot_df.empty:
    fig = px.scatter(
        plot_df,
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
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected plot.")




# --- Moon Map ---
# Turn location points into latitude/longitude pairs
import re

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

plot_df["Latitude"], plot_df["Longitude"] = zip(*plot_df["Location"].apply(parse_location))

# Load Moon map image
import base64
from io import BytesIO

def pil_to_base64_uri(pil_img):
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    base64_str = base64.b64encode(img_bytes).decode()
    return "data:image/png;base64," + base64_str

moon_img = mpimg.imread("C:/Users/gaste/OneDrive - ISAE-SUPAERO/supaero/RP/database/moon_map.jpg")
if moon_img.dtype != np.uint8:
    moon_img_pil = Image.fromarray((moon_img * 255).astype(np.uint8))
else:
    moon_img_pil = Image.fromarray(moon_img)

moon_img_uri = pil_to_base64_uri(moon_img_pil)

# Create scatter plot over the Moon map
fig = go.Figure()

for group in plot_df["Mission Group"].unique():
    df_group = plot_df[plot_df["Mission Group"] == group]
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

# Add moon image *after* scatter trace
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

# Lock axes exactly to image size and orientation
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
            standoff=20  # move y-axis title farther from axis ticks/image
        ),
        range=[-90, 90],
        constrain='domain',
        fixedrange=True,
        showgrid=False,
        zeroline=False,
    ),
    margin=dict(l=80, r=20, t=20, b=40),  # add margin for title and axis title
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    showlegend=True,
    legend=dict(
        title="Mission Group",
        y=0.8,       # vertical position of legend (1 = top of plot area)
        yanchor="top", 
        x=1,          # horizontal position (1 = right edge)
        xanchor="left",
    ),
    hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
    width=800,
    height=600
)

fig.update_xaxes(automargin=False)
fig.update_yaxes(automargin=False)

st.plotly_chart(fig, use_container_width=True, height=800)

st.markdown(
    "<hr><p style='font-size:11px; color:gray; text-align:center;'>© 2025 Lunar Regolith Database <br> Contact us at leonie.gasteiner@student.isae-supaero.fr</p>",
    unsafe_allow_html=True
)

