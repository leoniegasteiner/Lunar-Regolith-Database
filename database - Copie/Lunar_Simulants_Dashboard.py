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
    "Dataset_Simulants.csv",
    dtype=str,
    header=0,
    skip_blank_lines=False
    )
    df.columns =  ["Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Original source", "Link"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

# Load numerical data for plotting
@st.cache_data
def load_plot_data():
    df = pd.read_csv("Dataset_Simulants_plots.csv")
    df.columns =  [
        "Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Original source", "Link"
    ]
    numeric_cols = ["Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

db_df = load_database_data()
plot_df = load_plot_data()

st.title("Lunar Regolith Simulants Database")

# separate the different types of missions
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

db_df["Soil Group"] = db_df["Type of simulant"].apply(categorize_soil)



# --- Sidebar Filters ---
with st.sidebar:
    st.header("🔍 Filter Database")

    soil_group_filter = st.multiselect(
        "Select Type of Simulant", 
        options=["Mare", "Highland"]
    )
    
    test_filter = st.multiselect(
        "Select Test Type", 
        options=db_df["Test"].dropna().unique()
    )
    agency_filter = st.multiselect(
        "Select Agency",
        options=["NASA", "ESA", "JAXA", "KASA", "ISRO", "CNSA", "GISTDA"]
    )


filtered_db_df = db_df.copy()
if soil_group_filter:
    filtered_db_df = filtered_db_df[filtered_db_df["Soil Group"].isin(soil_group_filter)]
if test_filter:
    filtered_db_df = filtered_db_df[filtered_db_df["Test"].isin(test_filter)]
if agency_filter:
    filtered_db_df = filtered_db_df[filtered_db_df["Agency"].isin(agency_filter)]


# --- Display Database Table ---
st.subheader("Database Table")
st.dataframe(filtered_db_df)



# --- Plotting ---
st.subheader("Plot Numerical Data")


x_axis = st.selectbox("X-axis (categorical)", options=["Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)"])
y_axis = st.selectbox("Y-axis (numeric)", options=[
    "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
    "Cohesion (kPa)"
])

plot_df["Soil Group"] = plot_df["Type of simulant"].apply(categorize_soil)

#Marker shapes and colors for mission groups 
marker_shapes = {
    "Mare": "circle",
    "Highland": "square",
}

color_map = {
    "Mare": "#003f5c",   # deep blue
    "Highland": "#d45087",     # crimson red
    "Other": "#7a5195"     # purple
}


plot_df = plot_df.dropna(subset=[x_axis, y_axis])
if not plot_df.empty:
    fig = px.scatter(
        plot_df,
        x=x_axis,
        y=y_axis,
        color="Soil Group",
        symbol="Soil Group",
        color_discrete_map=color_map,
        symbol_map=marker_shapes,
        hover_data=["Simulant", x_axis, y_axis],
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
        legend_title_text="Soil Group",
        width=800,
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected plot.")



st.markdown(
    "<hr><p style='font-size:11px; color:gray; text-align:center;'>© 2025 Lunar Regolith Database <br> Contact us at leonie.gasteiner@student.isae-supaero.fr</p>",
    unsafe_allow_html=True
)


