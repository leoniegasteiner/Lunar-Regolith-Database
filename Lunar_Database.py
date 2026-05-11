#-------------------------------------------------------------------------------------------------------------------------------------------------------
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~LUNAR REGOLITH DATABASE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#--------------------------------------------------------------------------------------------------------------------------------------------------------
#Author: Léonie Gasteiner 
#Contact: gasteinerleonie@gmail.com

#Structure: 
# - Initialization: 15-228
# - Lunar Regolith Database Section: 235 - 1475
# - Lunar Simulants Database Section: 1480 - 2015
# - Lunar Samples Database Section: 2020 - 2235
# - Detailed Mission Pages Section: 2280 - 2360
# - Combined Data Section: 2365-2965
# - Footer: 2965-3000

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
import io
import importlib.util
from pathlib import Path

# ---- Make the database pretty ---------

#span accross the window

st.set_page_config(
    page_title="Lunar Regolith Database",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROMAN_NUMERAL_WORDS = {
    "i", "ii", "iii", "iv", "v",
    "vi", "vii", "viii", "ix", "x",
    "xi", "xii", "xiii", "xiv", "xv",
    "xvi", "xvii", "xviii", "xix", "xx",
}

def pretty_mission_name(raw_name: str) -> str:
    clean = raw_name.replace("_", " ").replace("-", " ").strip()
    words = clean.split()

    fixed_words = []
    for w in words:
        lw = w.lower()
        if lw in ROMAN_NUMERAL_WORDS:
            fixed_words.append(lw.upper())      
        else:
            fixed_words.append(w.capitalize())   
    return " ".join(fixed_words)

#------------------Functions -------------------

def categorize_mission(mission_name):
    if pd.isna(mission_name):
        return "Other"
    name = mission_name.lower()
    if "apollo" in name:
        return "Apollo"
    elif "orbiter" in name:
        return "LRO"
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
    if pd.isna(value):
        return (np.nan, np.nan)
    
    if isinstance(value, (int, float)):
        return (float(value), float(value))
    match = re.findall(r"[-+]?\d*\.?\d+", str(value))
    if len(match) == 0:
        return (np.nan, np.nan)
    try:
        numbers = [float(n) for n in match]
    except ValueError:
        return (np.nan, np.nan)
    if len(numbers) == 1:
        val = numbers[0]
        return (val, val)
    else:
        return (min(numbers), max(numbers))
    
def filter_numeric_range(df, col_min, col_max, min_val, max_val):
    return df[
        ((df[col_max].ge(min_val)) | (df[col_max].isna())) &
        ((df[col_min].le(max_val)) | (df[col_min].isna()))
    ]

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

def filter_numeric_range(df, col_min, col_max, min_val, max_val):
    """Filter keeping NaNs visible."""
    return df[
        ((df[col_max].ge(min_val)) | (df[col_max].isna())) &
        ((df[col_min].le(max_val)) | (df[col_min].isna()))
    ]

def add_watermark(fig):
    fig.add_annotation(
        text="2026 Lunar Regolith Database",
        xref="paper", yref="paper",
        x=1.0, y=1.02,          
        xanchor="right", yanchor="bottom",
        showarrow=False,
        font=dict(size=12, color="gray"),
        opacity=0.4             
    )
    return fig

# --------------- DATA LOADING SECTION ---------------

#Lunar Data Loading 
@st.cache_data
def load_database_data():
    df = pd.read_csv(
        "Dataset_Regolith.csv", 
        sep=";", 
        dtype=str, 
        header=0,
        skip_blank_lines=False,)
    df.columns = ["Mission", "Location", "Terrain", "Year", "Type of mission", "Test", "Test location", "Testing environment", "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Bearing capacity (kPa)", "Static bearing pressure (kPa)", "Normal stress range (kPa)", "Void ratio", "Density of grains (g/cm^3)", "Compressibility Coefficient", "Depth (cm)", "Specific gravity", "Porosity (%)", "Cone penetration resistance (kPa)", "Force applied (N)", "Sample ID", "Contact area (cm^2)", "Source", "Year of publication", "DOI / URL", "Comments"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    
    range_columns = [
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)",
        "Bearing capacity (kPa)", "Static bearing pressure (kPa)", "Normal stress range (kPa)", 
        "Void ratio", "Density of grains (g/cm^3)", "Compressibility Coefficient", 
        "Depth (cm)", "Specific gravity", "Porosity (%)", "Cone penetration resistance (kPa)", 
        "Force applied (N)", "Contact area (cm^2)", "Sample ID"
    ]
    
    for col in range_columns:
        if col in df.columns:
            extracted = df[col].apply(lambda x: pd.Series(extract_range(x)))
            df[f"min_{col}"] = pd.to_numeric(extracted[0], errors="coerce")
            df[f"max_{col}"] = pd.to_numeric(extracted[1], errors="coerce")
            df[f"avg_{col}"] = df[[f"min_{col}", f"max_{col}"]].mean(axis=1)
            
    df["Mission Group"] = df["Mission"].apply(categorize_mission)
            
    return df
lunar_db_df = load_database_data()


#Simulants Data Loading
@st.cache_data
def load_Simulants_data():
    df = pd.read_csv(
    "Dataset_Simulants.csv",
    dtype=str,
    header=0,
    skip_blank_lines=False,
    )
    df.columns =  ["Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Source","Year of publication","DOI / URL"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

simulant_db_df = load_Simulants_data()


#All data loading
@st.cache_data
def load_all_data():
    df = pd.read_csv(
    "Dataset_All.csv",
    sep=";",
    dtype=str,
    header=0,
    skip_blank_lines=False,
    )
    df.columns =  ["Mission / Simulant", "Developer", "Agency", "Moon Location", "Terrain", "Year", "Type of mission", "Test", "Test location", "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Bearing capacity (kPa)",  "Normal stress range (kPa)", "Void ratio", "Density of grains (g/cm^3)", "Compressibility Coefficient", "Depth (cm)", "Porosity (%)", "Force applied (N)", "Source","Year of publication", "DOI / URL", "Comments"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

all_db_df = load_all_data()

#Lunar Samples data loading 
@st.cache_data
def load_samples_data():
    df = pd.read_csv(
    "Dataset_Samples.csv",
    sep=";",
    dtype=str,
    header=0,
    skip_blank_lines=False,
    )
    df.columns =  ["Mission", "Sample", "Serial Number", "Return Container", "Container", "Sample Type", "Weight (g)", "Source"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

samples_db_df = load_samples_data()

#Samples PSD data loading 

@st.cache_data
def load_samples_PSD_data():
    df = pd.read_csv(
    "Dataset_Samples_PSD.csv",
    sep=";",
    dtype=str,
    header=0,
    skip_blank_lines=False,
    )
    df.columns =  ["Mission", "Sample", "Subsample", "depth (cm)", "Sieve size (µm)", "weight %", "D50 (µm)", "Source"]
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    return df

samples_PSD_db_df = load_samples_PSD_data()


db_choice = st.sidebar.radio(
    "Select Database:",
    ["Lunar Regolith Database", "Lunar Regolith Simulants Database", "Lunar Samples Database", "Detailed Mission Pages", "Combined Data"]
)

#visual 
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)



# --------------------------- Lunar Mission Database Section ---------------------------
if db_choice == "Lunar Regolith Database":

    st.title("Lunar Regolith Database")

   # Sidebar Filters
    def clear_all_filters():
        st.session_state["soil_group_filter"] = []
        st.session_state["test_filter"] = []
        st.session_state["mission_type_filter"] = []
        st.session_state["mission_group_filter"] = []
        st.session_state["test_location_filter"] = []
        st.session_state["testing_environment_filter"] = []
        st.session_state["year_range"] = (year_min, year_max)
        st.session_state["density_range"] = (round(dens_min, 2), round(dens_max, 2))
        st.session_state["cohesion_range"] = (round(coh_min, 1), round(coh_max, 1))
        st.session_state["angle_range"] = (round(ang_min, 1), round(ang_max, 1))
        st.session_state["static_bearing_range"] = (round(staticbc_min, 1), round(staticbc_max, 1))
        st.session_state["sbc_range"] = (round(sbc_min, 1), round(sbc_max, 1))
        st.session_state["ns_range"] = (round(nf_min, 1), round(nf_max, 1))
        st.session_state["vr_range"] = (round(vr_min, 2), round(vr_max, 2))
        st.session_state["dg_range"] = (round(dg_min, 2), round(dg_max, 2))
        st.session_state["cc_range"] = (round(cc_min, 4), round(cc_max, 4))
        st.session_state["depth_range"] = (round(depth_min, 1), round(depth_max, 1))
        st.session_state["specific_gravity_range"] = (round(sg_min, 2), round(sg_max, 2))
        st.session_state["por_range"] = (round(por_min, 1), round(por_max, 1))
        st.session_state["fa_range"] = (round(fa_min, 1), round(fa_max, 1))
        st.session_state["Contact area"] = (round(ca_min, 1), round(ca_max, 1))
        st.session_state["Sample ID"] = (round(sample_min, 1), round(sample_max, 1))
        st.session_state["selected_columns"] = [
            col for col in default_columns if col in lunar_db_df.columns
        ]

    with st.sidebar:
        st.header("Filter Regolith Data")
        with st.expander("Categorical Filters", expanded=False):
            st.markdown("### Terrain Type")
            soil_group_filter = st.multiselect("Select Terrain type", lunar_db_df["Terrain"].dropna().unique(), key="soil_group_filter")
            st.markdown("### Test Type")
            test_filter = st.multiselect("Select Test Type", lunar_db_df["Test"].dropna().unique(), key="test_filter")
            # --- Categorical Filters ---
            st.markdown("### Type of Mission")
            mission_type_filter = st.multiselect(
                "Select type of mission:",
                options=sorted(lunar_db_df["Type of mission"].dropna().unique()),
                key="mission_type_filter"
            )

            st.markdown("### Mission Group")
            mission_group_filter = st.multiselect(
                "Select Mission Group", 
                options=["Apollo", "Luna", "Surveyor", "Chang'e", "Chandrayaan", "Lunar Reconnaissance Orbiter", "Other"],
                key="mission_group_filter"
            )

            st.markdown("### Test Location")
            test_location_filter = st.multiselect(
                "Select Test Location", 
                options=["In-Situ", "On Earth", "Remote", "Other"],
                key="test_location_filter"
            )

            st.markdown("### Testing environment")
            testing_environment_filter = st.multiselect(
                "Select testing environment", 
                options=["Vacuum", "Air", "Nitrogen"],
                key = "testing_environment_filter"
            )

        # --- Numeric Range Filters ---
        with st.expander("Numeric Range Filters", expanded=False):
            year_range = None
            year_min = None 
            year_max = None
            st.markdown("### Publication Year")
            if "Year of publication" in lunar_db_df.columns:
                numeric_years = pd.to_numeric(lunar_db_df["Year of publication"], errors="coerce")
                year_min = int(numeric_years.min(skipna=True))
                year_max = int(numeric_years.max(skipna=True))

                if "year_range" not in st.session_state:
                    st.session_state["year_range"] = (year_min, year_max)

                year_range = st.slider(
                    "Select Year of publication Range",
                    min_value=year_min,
                    max_value=year_max,
                    key="year_range"
                )
            else:
                year_range = None


            st.markdown("### Density (g/cm³)")
            if "min_Bulk density (g/cm^3)" in lunar_db_df.columns:
                dens_min = float(lunar_db_df["min_Bulk density (g/cm^3)"].min(skipna=True))
                dens_max = float(lunar_db_df["max_Bulk density (g/cm^3)"].max(skipna=True))

                if "density_range" not in st.session_state:
                    st.session_state["density_range"] = (round(dens_min, 2), round(dens_max, 2))    

                density_range = st.slider(
                    "Select Density Range",
                    min_value=round(dens_min, 2),
                    max_value=round(dens_max, 2),
                    value=(round(dens_min, 2), round(dens_max, 2)),
                    key="density_range"
                )
            else:
                density_range = None

            st.markdown("### Cohesion (kPa)")
            if "min_Cohesion (kPa)" in lunar_db_df.columns:
                coh_min = float(lunar_db_df["min_Cohesion (kPa)"].min(skipna=True))
                coh_max = float(lunar_db_df["max_Cohesion (kPa)"].max(skipna=True))

                if "cohesion_range" not in st.session_state:
                    st.session_state["cohesion_range"] = (round(coh_min, 1), round(coh_max, 1))

                cohesion_range = st.slider(
                    "Select Cohesion Range",
                    min_value=round(coh_min, 1),
                    max_value=round(coh_max, 1),
                    value=(round(coh_min, 1), round(coh_max, 1)),
                    key="cohesion_range"
                )
            else:
                cohesion_range = None

            st.markdown("### Angle of Internal Friction (°)")
            if "min_Angle of internal friction (degree)" in lunar_db_df.columns:
                ang_min = float(lunar_db_df["min_Angle of internal friction (degree)"].min(skipna=True))
                ang_max = float(lunar_db_df["max_Angle of internal friction (degree)"].max(skipna=True))

                if "angle_range" not in st.session_state:
                    st.session_state["angle_range"] = (round(ang_min, 1), round(ang_max, 1))

                angle_range = st.slider(
                    "Select Angle Range",
                    min_value=round(ang_min, 1),
                    max_value=round(ang_max, 1),
                    value=(round(ang_min, 1), round(ang_max, 1)),
                    key="angle_range"
                )
            else:
                angle_range = None

            st.markdown("### Bearing Capacity (kPa)")
            if "min_Bearing capacity (kPa)" in lunar_db_df.columns:
                sbc_min = float(lunar_db_df["min_Bearing capacity (kPa)"].min(skipna=True))
                sbc_max = float(lunar_db_df["max_Bearing capacity (kPa)"].max(skipna=True))

                if "sbc_range" not in st.session_state:
                    st.session_state["sbc_range"] = (round(sbc_min, 1), round(sbc_max, 1))

                sbc_range = st.slider(
                   "Select Bearing Capacity Range",
                   min_value=round(sbc_min, 1),
                   max_value=round(sbc_max, 1),
                   value=(round(sbc_min, 1), round(sbc_max, 1)),
                   key="sbc_range"
               )
            else:
                sbc_range = None

            st.markdown("### Static Bearing Pressure (kPa)")
            if "min_Static bearing pressure (kPa)" in lunar_db_df.columns:
                staticbc_min = float(lunar_db_df["min_Static bearing pressure (kPa)"].min(skipna=True))
                staticbc_max = float(lunar_db_df["max_Static bearing pressure (kPa)"].max(skipna=True))

                if "static_bearing_range" not in st.session_state:
                    st.session_state["static_bearing_range"] = (round(staticbc_min, 1), round(staticbc_max, 1))

                static_bearing_range = st.slider(
                    "Select Static Bearing Pressure Range",
                    min_value=round(staticbc_min, 1),
                    max_value=round(staticbc_max, 1),
                    value=(round(staticbc_min, 1), round(staticbc_max, 1)),
                    key="static_bearing_range"
                )
            else:
                static_bearing_range = None

            st.markdown("### Normal Stress (kPa)")
            if "min_Normal stress range (kPa)" in lunar_db_df.columns:
                nf_min = float(lunar_db_df["min_Normal stress range (kPa)"].min(skipna=True))
                nf_max = float(lunar_db_df["max_Normal stress range (kPa)"].max(skipna=True))

                if "ns_range" not in st.session_state:
                    st.session_state["ns_range"] = (round(nf_min, 1), round(nf_max, 1))

                nf_range = st.slider(
                   "Select Normal Stress Range",
                   min_value=round(nf_min, 1),
                   max_value=round(nf_max, 1),
                   value=(round(nf_min, 1), round(nf_max, 1)),
                   key="ns_range"
               )
            else:
                nf_range = None

            st.markdown("### Void Ratio")
            if "min_Void ratio" in lunar_db_df.columns:
                vr_min = float(lunar_db_df["min_Void ratio"].min(skipna=True))
                vr_max = float(lunar_db_df["max_Void ratio"].max(skipna=True))

                if "vr_range" not in st.session_state:
                    st.session_state["vr_range"] = (round(vr_min, 2), round(vr_max, 2))

                vr_range = st.slider(
                   "Select Void Ratio Range",
                   min_value=round(vr_min, 2),
                   max_value=round(vr_max, 2),
                   value=(round(vr_min, 2), round(vr_max, 2)),
                   key="vr_range"
               )
            else:
                vr_range = None

            st.markdown("### Density of Grains (g/cm³)")
            if "min_Density of grains (g/cm^3)" in lunar_db_df.columns:
                dg_min = float(lunar_db_df["min_Density of grains (g/cm^3)"].min(skipna=True))
                dg_max = float(lunar_db_df["max_Density of grains (g/cm^3)"].max(skipna=True))

                if "dg_range" not in st.session_state:
                    st.session_state["dg_range"] = (round(dg_min, 2), round(dg_max, 2))

                dg_range = st.slider(
                   "Select Density of Grains Range",
                   min_value=round(dg_min, 2),
                   max_value=round(dg_max, 2),
                   value=(round(dg_min, 2), round(dg_max, 2)),
                   key="dg_range"
               )
            else:
                dg_range = None

            st.markdown("### Compressibility Coefficient")
            if "min_Compressibility Coefficient" in lunar_db_df.columns:
                cc_min = float(lunar_db_df["min_Compressibility Coefficient"].min(skipna=True))
                cc_max = float(lunar_db_df["max_Compressibility Coefficient"].max(skipna=True))

                if "cc_range" not in st.session_state:
                    st.session_state["cc_range"] = (round(cc_min, 4), round(cc_max, 4))

                cc_range = st.slider(
                   "Select Compressibility Coefficient Range",
                   min_value=round(cc_min, 4),
                   max_value=round(cc_max, 4),
                   value=(round(cc_min, 4), round(cc_max, 4)),
                   key="cc_range"
               )
            else:
                cc_range = None

            st.markdown("### Depth (cm)")
            if "min_Depth (cm)" in lunar_db_df.columns:
                depth_min = float(lunar_db_df["min_Depth (cm)"].min(skipna=True))
                depth_max = float(lunar_db_df["max_Depth (cm)"].max(skipna=True))

                if "depth_range" not in st.session_state:
                    st.session_state["depth_range"] = (round(depth_min, 1), round(depth_max, 1))

                depth_range = st.slider(
                   "Select Depth Range",
                   min_value=round(depth_min, 1),
                   max_value=round(depth_max, 1),
                   value=(round(depth_min, 1), round(depth_max, 1)),
                   key="depth_range"
               )
            else:
                depth_range = None  


            st.markdown("### Specific Gravity")
            if "min_Specific gravity" in lunar_db_df.columns:
                sg_min = float(lunar_db_df["min_Specific gravity"].min(skipna=True))
                sg_max = float(lunar_db_df["max_Specific gravity"].max(skipna=True))

                if "specific_gravity_range" not in st.session_state:
                    st.session_state["specific_gravity_range"] = (round(sg_min, 2), round(sg_max, 2))

                specific_gravity_range = st.slider(
                   "Select Specific Gravity Range",
                   min_value=round(sg_min, 2),
                   max_value=round(sg_max, 2),
                   value=(round(sg_min, 2), round(sg_max, 2)),
                   key="specific_gravity_range"
               )

            st.markdown("### Porosity (%)")
            if "min_Porosity (%)" in lunar_db_df.columns:
                por_min = float(lunar_db_df["min_Porosity (%)"].min(skipna=True))
                por_max = float(lunar_db_df["max_Porosity (%)"].max(skipna=True))

                if "por_range" not in st.session_state:
                    st.session_state["por_range"] = (round(por_min, 1), round(por_max, 1))

                por_range = st.slider(
                   "Select Porosity Range",
                   min_value=round(por_min, 1),
                   max_value=round(por_max, 1),
                   value=(round(por_min, 1), round(por_max, 1)),
                   key="por_range"
               )
            else:
                por_range = None

            st.markdown("### Force applied (N)")
            if "min_Force applied (N)" in lunar_db_df.columns:
                fa_min = float(lunar_db_df["min_Force applied (N)"].min(skipna=True))
                fa_max = float(lunar_db_df["max_Force applied (N)"].max(skipna=True))

                if "fa_range" not in st.session_state:
                    st.session_state["fa_range"] = (round(fa_min, 1), round(fa_max, 1))

                fa_range = st.slider(
                   "Select Force applied Range",
                   min_value=round(fa_min, 1),
                   max_value=round(fa_max, 1),
                   value=(round(fa_min, 1), round(fa_max, 1)),
                   key="fa_range"
               )
            else:
                fa_range = None

            st.markdown("### Contact area")
            if "min_Contact area (cm^2)" in lunar_db_df.columns:
                ca_min = float(lunar_db_df["min_Contact area (cm^2)"].min(skipna=True))
                ca_max = float(lunar_db_df["max_Contact area (cm^2)"].max(skipna=True))

                if "fa_range" not in st.session_state:
                    st.session_state["ca_range"] = (round(ca_min, 1), round(ca_max, 1))

                ca_range = st.slider(
                   "Select Contact area Range",
                   min_value=round(ca_min, 1),
                   max_value=round(ca_max, 1),
                   value=(round(ca_min, 1), round(ca_max, 1)),
                   key="ca_range"
               )
            else:
                ca_range = None

            st.markdown("### Sample ID")
            if "min_Sample ID" in lunar_db_df.columns:
                sample_min = float(lunar_db_df["min_Sample ID"].min(skipna=True))
                sample_max = float(lunar_db_df["max_Sample ID"].max(skipna=True))

                if "fa_range" not in st.session_state:
                    st.session_state["sample_range"] = (round(sample_min, 1), round(sample_max, 1))

                sample_range = st.slider(
                   "Select Sample ID Range",
                   min_value=round(sample_min, 1),
                   max_value=round(sample_max, 1),
                   value=(round(sample_min, 1), round(sample_max, 1)),
                   key="sample_range"
               )
            else:
                sample_range = None

        # --- Column Selection ---
        with st.expander("Select Table Columns", expanded=False):
            st.divider()
            st.header("Display Options")
            all_columns = lunar_db_df.columns.tolist()
            default_columns = [
        "Mission", "Location", "Terrain","Year","Type of mission","Test", "Test location", "Testing environment",
        "Bulk density (g/cm^3)",
        "Angle of internal friction (degree)", 
        "Cohesion (kPa)", 
        "Bearing capacity (kPa)", "Depth (cm)", "Sample ID",
        "Static bearing pressure (kPa)", "Normal stress range (kPa)", "Void ratio", "Density of grains (g/cm^3)", "Compressibility Coefficient", "Specific gravity", "Porosity (%)", "Cone penetration resistance (kPa)", "Force applied (N)", "Contact area (cm^2)", 
        "Source","Year of publication", "DOI / URL", "Comments"]        


            def select_all_columns():
                st.session_state["selected_columns"] = all_columns

            def clear_columns():
                st.session_state["selected_columns"] = default_columns

            col_select_all, col_clear_selection = st.columns([1, 1])

            with col_select_all:
                st.button(
                    "Select All Parameters", 
                    on_click=select_all_columns, 
                    use_container_width=True
                )

            with col_clear_selection:
                 st.button(
                    "Clear Selection", 
                    on_click=clear_columns, 
                    use_container_width=True
                )

            selected_columns = st.multiselect(
                "Select columns to display:",
                options=all_columns,
                default=[col for col in default_columns if col in all_columns],
                key="selected_columns"
            )

        st.button("Clear all filters", use_container_width=True, on_click=clear_all_filters)



    # --- Apply Filters ---
    filtered_db_df = lunar_db_df.copy()
    numeric_cols = [
    "Year of publication",
    "Bulk density (g/cm^3)",
    "Angle of internal friction (degree)",
    "Cohesion (kPa)",
    "Bearing capacity (kPa)",
    "Static bearing pressure (kPa)",
    "Normal stress range (kPa)",
    "Void ratio",
    "Density of grains (g/cm^3)",
    "Compressibility Coefficient",
    "Depth (cm)",
    "Specific gravity",
    "Porosity (%)",
    "Force applied (N)",
    "Contact area (cm^2)", 
    "Sample ID", 
    "Year"
    ]

    for col in numeric_cols:
        if col in filtered_db_df.columns:
            filtered_db_df[col] = pd.to_numeric(filtered_db_df[col], errors="coerce")

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

    # Test location filter
    if test_location_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Test location"].isin(test_location_filter)]
    
    # Testing environment filter
    if testing_environment_filter: 
        filtered_db_df = filtered_db_df[filtered_db_df["Testing environment"].isin(testing_environment_filter)]

    # Year of publication filter (only if slider active)
    if year_range and isinstance(year_range, tuple) and (year_range != (year_min, year_max)):
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Year of publication"] >= year_range[0]) &
            (filtered_db_df["Year of publication"] <= year_range[1])
        ]


    # --- Numeric filters ---
    if density_range and (density_range != (round(dens_min, 2), round(dens_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Bulk density (g/cm^3)", "max_Bulk density (g/cm^3)",
            density_range[0], density_range[1]
        )


    if cohesion_range and (cohesion_range != (round(coh_min, 2), round(coh_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Cohesion (kPa)", "max_Cohesion (kPa)",
            cohesion_range[0], cohesion_range[1]
        )

    if angle_range and (angle_range != (round(ang_min, 2), round(ang_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Angle of internal friction (degree)", "max_Angle of internal friction (degree)",
            angle_range[0], angle_range[1]
        )

    if sbc_range and (sbc_range != (round(sbc_min, 2), round(sbc_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Bearing capacity (kPa)", "max_Bearing capacity (kPa)",
            sbc_range[0], sbc_range[1]
        )

    if static_bearing_range and (static_bearing_range != (round(staticbc_min, 2), round(staticbc_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Static bearing pressure (kPa)", "max_Static bearing pressure (kPa)",
            static_bearing_range[0], static_bearing_range[1]
        )

    if nf_range and (nf_range != (round(nf_min, 2), round(nf_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Normal stress range (kPa)", "max_Normal stress range (kPa)",
            nf_range[0], nf_range[1]
        )

    if vr_range and (vr_range != (round(vr_min, 2), round(vr_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Void ratio", "max_Void ratio",
            vr_range[0], vr_range[1]
        )
    
    if dg_range and (dg_range != (round(dg_min, 2), round(dg_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Density of grains (g/cm^3)", "max_Density of grains (g/cm^3)",
            dg_range[0], dg_range[1]
        )

    if cc_range and (cc_range != (round(cc_min, 4), round(cc_max, 4))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Compressibility Coefficient", "max_Compressibility Coefficient",
            cc_range[0], cc_range[1]
        )
    
    if depth_range and (depth_range != (round(depth_min, 2), round(depth_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Depth (cm)", "max_Depth (cm)",
            depth_range[0], depth_range[1]
        )

    if specific_gravity_range and (specific_gravity_range != (round(sg_min, 2), round(sg_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Specific gravity", "max_Specific gravity",
            specific_gravity_range[0], specific_gravity_range[1]
        )

    if por_range and (por_range != (round(por_min, 2), round(por_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Porosity (%)", "max_Porosity (%)",
            por_range[0], por_range[1]
        )

    if fa_range and (fa_range != (round(fa_min, 2), round(fa_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Force applied (N)", "max_Force applied (N)",
            fa_range[0], fa_range[1]
        )

    if ca_range and (ca_range != (round(ca_min, 2), round(ca_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Contact area (cm^2)", "max_Contact area (cm^2)",
            ca_range[0], ca_range[1]
        )

    if sample_range and (sample_range != (round(sample_min, 2), round(sample_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Sample ID", "max_Sample ID",
            sample_range[0], sample_range[1]
        )
    

    display_df = filtered_db_df.copy()

    numeric_range_cols = [
        "Bulk density (g/cm^3)",
        "Angle of internal friction (degree)",
        "Cohesion (kPa)",
        "Bearing capacity (kPa)",
        "Static bearing pressure (kPa)",
        "Normal stress range (kPa)",
        "Void ratio",
        "Density of grains (g/cm^3)",
        "Compressibility Coefficient",
        "Depth (cm)",
        "Specific gravity",
        "Porosity (%)",
        "Force applied (N)", 
        "Contact area (cm^2)", 
        "Sample ID"
    ]

    for col in numeric_range_cols:
        # Keep _min, _max, _avg numeric
        if col in display_df.columns:
            display_df[col] = lunar_db_df.loc[display_df.index, col]

    # --- Display filtered table ---
    st.subheader("Database Table")
    if selected_columns:
        st.dataframe(display_df[selected_columns])
    else:
        st.info("No columns selected. Please select at least one column to display.")

    st.markdown(
        "<p style='font-size:12px; color:gray;'>Note: * Indicates values estimated for the measurements, ** indicates values derived from estimations. </p>",
        unsafe_allow_html=True
    )

    st.info("Select ""table columns"" to tailor parameter display")


    # --- Plotting Section & Display ---
    st.subheader("Plot Numerical Data")

    # Select axes
    x_axis = st.selectbox("X-axis (categorical & numeric)", options=[
        "Mission", "Location", "Terrain", "Test", "Type of mission", "Testing environment",
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Bearing capacity (kPa)", "Static bearing pressure (kPa)", "Normal stress range (kPa)", 
        "Void ratio", "Density of grains (g/cm^3)", "Compressibility Coefficient", "Depth (cm)", "Specific gravity", "Porosity (%)", 
        "Force applied (N)", "Contact area (cm^2)", "Sample ID", "Year of publication"
    ])
    y_axis = st.selectbox("Y-axis (numeric)", options=[
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", 
        "Cohesion (kPa)", "Bearing capacity (kPa)", "Static bearing pressure (kPa)", "Normal stress range (kPa)", 
        "Void ratio", "Density of grains (g/cm^3)", "Compressibility Coefficient", "Depth (cm)", "Specific gravity", "Porosity (%)", 
        "Force applied (N)", "Contact area (cm^2)", "Year of publication"
    ])
    plot_mode = st.radio("Select value type to plot", ["Range", "Average", "Minimum", "Maximum"], horizontal=True)

    legend_column = st.selectbox("Select Legend", options=[
    "Mission Group", 
    "Terrain", 
    "Type of mission", 
    "Test location",
    "Test", 
    "Testing environment"
    ], index=0)

    lunar_db_df["Mission Group"] = lunar_db_df["Mission"].apply(categorize_mission)
    

    range_columns = [
        "Bulk density (g/cm^3)",
        "Angle of internal friction (degree)",
        "Cohesion (kPa)",
        "Bearing capacity (kPa)", 
        "Static bearing pressure (kPa)",
        "Normal stress range (kPa)",
        "Void ratio",
        "Density of grains (g/cm^3)",
        "Compressibility Coefficient",
        "Depth (cm)",
        "Specific gravity",
        "Porosity (%)",
        "Force applied (N)", 
        "Contatct area (cm^2)"
    ]            

    for col in range_columns:
        if col in lunar_db_df.columns:
            lunar_db_df[[f"min_{col}", f"max_{col}"]] = lunar_db_df[col].apply(
                lambda x: pd.Series(extract_range(x))
            )
            lunar_db_df[[f"min_{col}", f"max_{col}"]] = lunar_db_df[
                [f"min_{col}", f"max_{col}"]
            ].apply(pd.to_numeric, errors="coerce")
            lunar_db_df[f"avg_{col}"] = lunar_db_df[[f"min_{col}", f"max_{col}"]].mean(axis=1)

    # --- Apply filters ---
    filtered_plot_df = lunar_db_df.copy()
    filtered_plot_df["Year of publication"] = pd.to_numeric(filtered_plot_df["Year of publication"], errors="coerce")

    if mission_group_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Mission Group"].isin(mission_group_filter)]
    if test_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Test"].isin(test_filter)]
    if soil_group_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Terrain"].isin(soil_group_filter)]
    if mission_type_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Type of mission"].isin(mission_type_filter)]
    if test_location_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Test location"].isin(test_location_filter)]
    if testing_environment_filter: 
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Testing environment"].isin(testing_environment_filter)]

    # --- Numeric filters ---
    
    if year_range and isinstance(year_range, tuple) and (year_range != (year_min, year_max)):
        filtered_plot_df = filtered_plot_df[
            (filtered_plot_df["Year of publication"] >= year_range[0]) &
            (filtered_plot_df["Year of publication"] <= year_range[1])
        ]


    if density_range and (density_range != (round(dens_min, 2), round(dens_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Bulk density (g/cm^3)", "max_Bulk density (g/cm^3)",
            density_range[0], density_range[1]
        )

    if cohesion_range and (cohesion_range != (round(coh_min, 2), round(coh_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Cohesion (kPa)", "max_Cohesion (kPa)",
            cohesion_range[0], cohesion_range[1]
        )

    if angle_range and (angle_range != (round(ang_min, 2), round(ang_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Angle of internal friction (degree)", "max_Angle of internal friction (degree)",
            angle_range[0], angle_range[1]
        )

    if sbc_range and (sbc_range != (round(sbc_min, 2), round(sbc_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Bearing capacity (kPa)", "max_Bearing capacity (kPa)",
            sbc_range[0], sbc_range[1]
        )

    if static_bearing_range and (static_bearing_range != (round(staticbc_min, 2), round(staticbc_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Static bearing pressure (kPa)", "max_Static bearing pressure (kPa)",
            static_bearing_range[0], static_bearing_range[1]
        )

    if nf_range and (nf_range != (round(nf_min, 2), round(nf_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Normal stress range (kPa)", "max_Normal stress range (kPa)",
            nf_range[0], nf_range[1]
        )

    if vr_range and (vr_range != (round(vr_min, 2), round(vr_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Void ratio", "max_Void ratio",
            vr_range[0], vr_range[1]
        )   

    if dg_range and (dg_range != (round(dg_min, 2), round(dg_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Density of grains (g/cm^3)", "max_Density of grains (g/cm^3)",
            dg_range[0], dg_range[1]
        )

    if cc_range and (cc_range != (round(cc_min, 4), round(cc_max, 4))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Compressibility Coefficient", "max_Compressibility Coefficient",
            cc_range[0], cc_range[1]
        )

    if depth_range and (depth_range != (round(depth_min, 2), round(depth_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Depth (cm)", "max_Depth (cm)",
            depth_range[0], depth_range[1]
        )

    if specific_gravity_range and (specific_gravity_range != (round(sg_min, 2), round(sg_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Specific gravity", "max_Specific gravity",
            specific_gravity_range[0], specific_gravity_range[1]
        )

    if por_range and (por_range != (round(por_min, 2), round(por_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Porosity (%)", "max_Porosity (%)",
            por_range[0], por_range[1]
        )

    if fa_range and (fa_range != (round(fa_min, 2), round(fa_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Force applied (N)", "max_Force applied (N)",
            fa_range[0], fa_range[1]
        )

    if ca_range and (ca_range != (round(ca_min, 2), round(ca_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Contact area (cm^2)", "max_Contact area (cm^2)",
            ca_range[0], ca_range[1]
        )


    # Define colors and markers

    def get_plot_maps(column):
    # Base colors/shapes for mission group
        mission_color_map = {
            "Apollo": "#0b96d6", "Luna": "#d45087", "Surveyor": "#ffa600", 
            "Chang'e": "#72CF6D", "Chandrayaan": "#8d3ab0", "Other": "gray"
        }
        mission_marker_shapes = {
            "Apollo": "circle", "Luna": "square", "Surveyor": "triangle-up",
            "Chang'e": "diamond", "Chandrayaan": "cross", "Other": "x"
        }

        if column == "Mission Group":
            return mission_color_map, mission_marker_shapes

        if column == "Terrain":
            return {"Mare": "#1f77b4", "Highland": "#ff7f0e", "Other": "#2ca02c"}, {"Mare": "circle", "Highland": "square", "Other": "cross"}
        if column == "Type of mission":
            return {"Lander": "#1f77b4", "Rover": "#ff7f0e", "Crewed": "#2ca02c", "Other": "#9467bd"}, {"Lander": "circle", "Rover": "square", "Crewed": "diamond", "Other": "x"}
        if column == "Test location":
            return {"In-Situ": "#1f77b4", "On Earth": "#ff7f0e", "Other": "#2ca02c"}, {"In-Situ": "circle", "On Earth": "square", "Other": "diamond"}
        if column == "Test":
            unique_tests = filtered_plot_df["Test"].dropna().unique()
            default_colors = px.colors.qualitative.Plotly
            color_map = {}
            marker_shapes = {}
            for i, test in enumerate(unique_tests):
                color_map[test] = default_colors[i % len(default_colors)]
                marker_shapes[test] = "circle"  # Default shape
            return color_map, marker_shapes
        if column == "Testing environment":
            return {"Vacuum": "#1f77b4", "Air": "#ff7f0e", "Nitrogen": "#2ca02c"}, {"Vacuum": "circle", "Air": "square", "Nitrogen": "diamond"}
        return mission_color_map, mission_marker_shapes


    color_map, marker_shapes = get_plot_maps(legend_column)

    # --- Determine Y columns ---
    y_min_col = f"min_{y_axis}"
    y_max_col = f"max_{y_axis}"
    y_col_map = {
        "Average": f"avg_{y_axis}",
        "Minimum": y_min_col,
        "Maximum": y_max_col,
        "Range": y_axis
    }
    y_col_name = y_col_map[plot_mode]

    x_axis_is_numeric = x_axis in range_columns

    if plot_mode == "Range":
        filtered_plot_df = filtered_plot_df.dropna(subset=[y_min_col, y_max_col])
        if x_axis_is_numeric:
            # Also need x-axis range columns
            x_min_col = f"min_{x_axis}"
            x_max_col = f"max_{x_axis}"
            filtered_plot_df = filtered_plot_df.dropna(subset=[x_min_col, x_max_col])
    else:
        filtered_plot_df = filtered_plot_df.dropna(subset=[y_col_name])


    #Compare with simulant button
    required_x_col = x_axis
    required_y_col = y_axis

    if required_x_col in simulant_db_df.columns and required_y_col in simulant_db_df.columns:
        compare_simulants = st.checkbox("Compare with lunar regolith simulants")
    else:
        compare_simulants = False


     # --- RANGE MODE PLOTTING ---
    if plot_mode == "Range":
        fig = go.Figure()

        # For categorical x-axis, create position mapping
        if not x_axis_is_numeric:
            x_categories = filtered_plot_df[x_axis].dropna().unique()
            x_positions = {val: idx for idx, val in enumerate(x_categories)}

        legend_groups = set()

        if color_map is None:
            color_map = {}
            unique_groups = filtered_plot_df[legend_column].dropna().unique()
            default_colors = px.colors.qualitative.Plotly
            for i, group in enumerate(unique_groups):
                color_map[group] = default_colors[i % len(default_colors)]

        for _, row in filtered_plot_df.iterrows():
            group = row[legend_column]
            color = color_map.get(group, "gray")

            # --- Handle X-axis positioning ---
            if x_axis_is_numeric:
                # X-axis is numeric: use actual range values
                x_min_col = f"min_{x_axis}"
                x_max_col = f"max_{x_axis}"
                x_min = row[x_min_col]
                x_max = row[x_max_col]

                if pd.isna(x_min) or pd.isna(x_max):
                    continue
                
                x_display = f"{x_min:.2f}–{x_max:.2f}"
            else:
                # X-axis is categorical: use position with small width
                x_val = row[x_axis]
                if pd.isna(x_val) or x_val not in x_positions:
                    continue
                
                x_pos = x_positions[x_val]
                x_min = x_pos - 0.35
                x_max = x_pos + 0.35
                x_display = str(x_val)

            # --- Handle Y-axis range ---
            y_min = row[y_min_col]
            y_max = row[y_max_col]

            if pd.isna(y_min) or pd.isna(y_max):
                continue
            
            # Rectangle coordinates
            x_coords = [x_min, x_max, x_max, x_min, x_min]
            y_coords = [y_min, y_min, y_max, y_max, y_min]

            # --- Draw filled rectangle ---
            show_legend = group not in legend_groups
            legend_groups.add(group)

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                fill="toself",
                fillcolor=color,
                line=dict(color=color, width=2),
                opacity=0.5,
                name=group,
                legendgroup=group,
                showlegend=show_legend,
                hoverinfo="text",
                hovertext=(
                    f"Mission: {row['Mission']}<br>"
                    f"{x_axis}: {x_display}<br>"
                    f"{y_axis}: {y_min:.2f}–{y_max:.2f}<br>"
                    f"Group: {group}"
                )
            ))

        # --- Update layout based on x-axis type ---
        if x_axis_is_numeric:
            fig.update_layout(
                xaxis=dict(
                    title=x_axis,
                    type="linear",
                    tickformat=".2f"
                )
            )
        else:
            fig.update_layout(
                xaxis=dict(
                    title=x_axis,
                    tickmode="array",
                    tickvals=list(range(len(x_categories))),
                    ticktext=list(x_categories)
                )
            )

        fig.update_layout(
            title=f"{y_axis} Range vs {x_axis} Range",
            yaxis=dict(title=y_axis, tickformat=".2f"),
            height=600,
            width=800,
            hovermode="closest",
            legend_title_text=legend_column,
        )


    # --- SCATTER PLOT MODES (Average, Min, Max) ---
    else:
        if x_axis in range_columns:
            x_col_map = {
                "Average": f"avg_{x_axis}",
                "Minimum": f"min_{x_axis}",
                "Maximum": f"max_{x_axis}",
            }
            x_col_name = x_col_map.get(plot_mode, x_axis) 
        else:
            x_col_name = x_axis

        fig = px.scatter(
            filtered_plot_df,
            x=x_col_name,
            y=y_col_name,
            color=legend_column,
            symbol=legend_column,
            color_discrete_map=color_map,
            symbol_map=marker_shapes,
            hover_data={"Mission": True, x_col_name: ":.2f", y_col_name: ":.2f", legend_column: True},
            title=f"{plot_mode} {y_axis} vs {plot_mode} {x_axis}" if x_axis in range_columns else f"{plot_mode} {y_axis} vs {x_axis}",
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        if x_axis in range_columns or x_axis == "Year of publication":
            fig.update_xaxes(type='linear', tickformat=".2f")

        fig.update_layout(
            xaxis_title=f"{plot_mode} {x_axis}" if x_axis in range_columns else x_axis,
            yaxis_title=f"{plot_mode}{y_axis}",
            hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
            title=dict(x=0, xanchor='left', font=dict(size=20)),
            legend_title_text=legend_column,
            width=800,
            height=500,
        )

    # --- Add simulant data if selected ---
    if compare_simulants:
        simulant_plot_df = simulant_db_df.copy()
        for col in range_columns:
            if col in simulant_plot_df.columns:
                simulant_plot_df[[f"min_{col}", f"max_{col}"]] = simulant_plot_df[col].apply(
                    lambda x: pd.Series(extract_range(x))
                )
                simulant_plot_df[[f"min_{col}", f"max_{col}"]] = simulant_plot_df[
                    [f"min_{col}", f"max_{col}"]
                ].apply(pd.to_numeric, errors="coerce")
                simulant_plot_df[f"avg_{col}"] = simulant_plot_df[[f"min_{col}", f"max_{col}"]].mean(axis=1)
        
        if plot_mode == "Range":
            y_min_col_sim = y_min_col
            y_max_col_sim = y_max_col

            if y_min_col_sim in simulant_plot_df.columns and y_max_col_sim in simulant_plot_df.columns:
                sim_filtered = simulant_plot_df.dropna(subset=[y_min_col_sim, y_max_col_sim])
                
                if x_axis in sim_filtered.columns:
                    x_min_col_sim = f"min_{x_axis}"
                    x_max_col_sim = f"max_{x_axis}"

                    if x_axis_is_numeric and x_min_col_sim in sim_filtered.columns and x_max_col_sim in sim_filtered.columns:
                        sim_filtered = sim_filtered.dropna(subset=[x_min_col_sim, x_max_col_sim])

                    simulant_legend_added = False
                    
                    for _, row in sim_filtered.iterrows():
                        # --- Handle X positioning ---
                        if x_axis_is_numeric:
                            x_min = row[x_min_col_sim]
                            x_max = row[x_max_col_sim]
                            if pd.isna(x_min) or pd.isna(x_max):
                                continue
                            x_display = f"{x_min:.2f}–{x_max:.2f}"
                        else:
                            x_val = row[x_axis]
                            if 'x_positions' not in locals(): continue
                            if pd.isna(x_val) or x_val not in x_positions:
                                continue
                            x_pos = x_positions[x_val]
                            x_min = x_pos - 0.35
                            x_max = x_pos + 0.35
                            x_display = str(x_val)
                        
                        # --- Handle Y range ---
                        y_min = row[y_min_col_sim]
                        y_max = row[y_max_col_sim]
                        if pd.isna(y_min) or pd.isna(y_max):
                            continue
                        
                        x_coords = [x_min, x_max, x_max, x_min, x_min]
                        y_coords = [y_min, y_min, y_max, y_max, y_min]
                        
                        fig.add_trace(go.Scatter(
                            x=x_coords,
                            y=y_coords,
                            fill="toself",
                            fillcolor="#ff00ff",
                            line=dict(color="#ff00ff", width=2),
                            opacity=0.3,
                            name="Lunar Simulants",
                            legendgroup="simulants",
                            showlegend=not simulant_legend_added,
                            hoverinfo="text",
                            hovertext=(
                                f"Simulant: {row['Simulant']}<br>"
                                f"{x_axis}: {x_display}<br>"
                                f"{y_axis}: {y_min:.2f}–{y_max:.2f}"
                            )
                        ))
                        simulant_legend_added = True
        
        else:
            # Scatter mode - add simulant points
            if x_axis in simulant_plot_df.columns and y_col_name in simulant_plot_df.columns:
                sim_scatter = simulant_plot_df.dropna(subset=[x_axis, y_col_name])
                
                hover_texts = [
                    f"Simulant: {row['Simulant']}<br>{x_axis}: {row[x_axis]}<br>{y_axis}: {row[y_col_name]:.2f}"
                    for _, row in sim_scatter.iterrows()
                ]
                
                fig.add_scatter(
                    x=sim_scatter[x_axis],
                    y=sim_scatter[y_col_name],
                    mode="markers",
                    name="Lunar Simulants",
                    marker=dict(symbol="diamond", size=10, color="#ff00ff", line=dict(width=1, color="black")),
                    hovertext=hover_texts,
                    hoverinfo="text"
                )
            else:
                st.warning(f"Required columns not found in simulant dataset for comparison.")
   
    # --- Display plot ---
    config = {"displayModeBar": False, "scrollZoom": True}
    # Watermark
    add_watermark(fig)
    st.plotly_chart(fig, width='stretch', config=config)


# ------------------ Moon Map --------------

    st.subheader("Mission Location Representation on the Moon")

    if "Latitude" not in lunar_db_df.columns or "Longitude" not in lunar_db_df.columns:
        if not lunar_db_df.empty:
            lunar_db_df["Latitude"], lunar_db_df["Longitude"] = zip(*lunar_db_df["Location"].apply(parse_location))
        else:
            lunar_db_df["Latitude"] = pd.Series(dtype=float)
            lunar_db_df["Longitude"] = pd.Series(dtype=float)
    
    map_df = filtered_db_df.copy()
    

    if "Latitude" not in map_df.columns or "Longitude" not in map_df.columns:
        if not map_df.empty:
            map_df["Latitude"], map_df["Longitude"] = zip(*map_df["Location"].apply(parse_location))
        else:
            map_df["Latitude"] = pd.Series(dtype=float)
            map_df["Longitude"] = pd.Series(dtype=float)

    map_df = map_df.dropna(subset=["Latitude", "Longitude"])
    
    map_legend_column = locals().get('legend_column', "Mission Group") 
    
    try:
        color_map, marker_shapes = get_plot_maps(map_legend_column)
    except NameError:
        map_legend_column = "Mission Group"
        color_map = {
             "Apollo": "#0b96d6", "Luna": "#d45087", "Surveyor": "#ffa600", 
             "Chang'e": "#72CF6D", "Chandrayaan": "#8d3ab0", "Other": "gray"
        }
        marker_shapes = {
            "Apollo": "circle", "Luna": "square", "Surveyor": "triangle-up",
            "Chang'e": "diamond", "Chandrayaan": "cross", "Other": "x"
        }

    if color_map is None:
        color_map = {}
        unique_groups = map_df[map_legend_column].dropna().unique()
        default_colors = px.colors.qualitative.Plotly
        for i, group in enumerate(unique_groups):
            color_map[group] = default_colors[i % len(default_colors)]

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


    for group in map_df[map_legend_column].unique():
        df_group = map_df[map_df[map_legend_column] == group]

        color = color_map.get(group, "black")
        symbol = marker_shapes.get(group, "circle") 

        hover_text = df_group.apply(
            lambda row: (
                f"Mission: {row['Mission']}<br>"
                f"Terrain: {row['Terrain']}<br>"
                f"Longitude: {row['Longitude']}°<br>"
                f"Latitude: {row['Latitude']}°"
            ), 
            axis=1
        )
        fig.add_trace(go.Scatter(
            x=df_group["Longitude"],
            y=df_group["Latitude"],
            mode="markers",
            marker=dict(
                size=10,
                # 4. Use dynamic color and symbol
                color=color,
                symbol=symbol,
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
            # 5. Use dynamic legend title
            title=map_legend_column,
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
    st.plotly_chart(fig, width='stretch', height=800, config=config_map)



## --------------------------- Lunar Simulants Database Section ---------------------------

elif db_choice == "Lunar Regolith Simulants Database":

    st.title("Lunar Regolith Simulants Database")
    simulant_db_df.columns = simulant_db_df.columns.str.strip()
    numeric_cols = ["Year", "Year of publication"]
    for col in numeric_cols:
        if col in simulant_db_df.columns:
            simulant_db_df[col] = pd.to_numeric(simulant_db_df[col], errors="coerce")

    range_columns = [
        "Bulk density (g/cm^3)",
        "Angle of internal friction (degree)",
        "Cohesion (kPa)",
    ]

    simulant_db_df["Soil Group"] = simulant_db_df["Type of simulant"].apply(categorize_soil)

    for col in range_columns:
        if col in simulant_db_df.columns:
            simulant_db_df[[f"min_{col}", f"max_{col}"]] = simulant_db_df[col].apply(
                lambda x: pd.Series(extract_range(x))
            )
            simulant_db_df[f"avg_{col}"] = simulant_db_df[
                [f"min_{col}", f"max_{col}"]
            ].mean(axis=1)

        # Sidebar Filters
    def clear_all_filters():
        st.session_state["soil_group_filter"] = []
        st.session_state["test_filter"] = []
        st.session_state["agency_filter"] = []
        st.session_state["developer_filter"] = []
        st.session_state["year_range"] = (year_min, year_max)
        st.session_state["density_range"] = (round(dens_min, 2), round(dens_max, 2))
        st.session_state["cohesion_range"] = (round(coh_min, 1), round(coh_max, 1))
        st.session_state["angle_range"] = (round(ang_min, 1), round(ang_max, 1))
        st.session_state["simulant_selected_columns"] = [
            col for col in default_columns if col in simulant_db_df.columns
        ]


    with st.sidebar:
            st.header("Filter Simulant Data")
            #original filters 
            with st.expander("Categorical Filters", expanded=False):
                st.markdown("### Type of Simulant")
                soil_group_filter = st.multiselect("Select Type of Simulant", ["Mare", "Highland", "Other"], key="soil_group_filter")
                st.markdown("### Test Type")
                test_filter = st.multiselect("Select Test Type", simulant_db_df["Test"].dropna().unique(), key="test_filter")
                st.markdown("### Agency")
                agency_filter = st.multiselect("Select Agency", ["NASA", "ESA", "JAXA", "KASA", "ISRO", "CNSA", "GISTDA"], key="agency_filter")
                st.markdown("### Developer")
                developer_filter = st.multiselect(
                    "Select Developer(s):",
                    options=sorted(simulant_db_df["Developer"].dropna().unique()), key="developer_filter")


            # --- Numeric Range Filters ---
            with st.expander("Numeric Range Filters", expanded=False):
                st.markdown("### Publication Year")
                if "Year of publication" in simulant_db_df.columns:
                    numeric_years = pd.to_numeric(simulant_db_df["Year of publication"], errors="coerce")
                    year_min, year_max = int(numeric_years.min(skipna=True)), int(numeric_years.max(skipna=True))

                    if "year_range" not in st.session_state:
                        st.session_state["year_range"] = (year_min, year_max)

                    year_range = st.slider(
                        "Select Year of publication Range",
                        min_value=year_min,
                        max_value=year_max,
                        key="year_range"
                    )
                else:
                    year_range = None

                st.markdown("### Density (g/cm³)")
                if "Bulk density (g/cm^3)" in simulant_db_df.columns:
                    dens_min, dens_max = float(simulant_db_df["min_Bulk density (g/cm^3)"].min(skipna=True)), float(simulant_db_df["max_Bulk density (g/cm^3)"].max(skipna=True))

                    if "density_range" not in st.session_state:
                        st.session_state["density_range"] = (round(dens_min, 2), round(dens_max, 2))

                    density_range = st.slider(
                        "Select Density Range",
                        min_value=round(dens_min, 2),
                        max_value=round(dens_max, 2),
                        value=st.session_state["density_range"],
                        key="density_range")
                else:
                    density_range = None

                st.markdown("### Cohesion (kPa)")
                if "Cohesion (kPa)" in simulant_db_df.columns:
                    coh_min, coh_max = float(simulant_db_df["min_Cohesion (kPa)"].min(skipna=True)), float(simulant_db_df["max_Cohesion (kPa)"].max(skipna=True))

                    if "cohesion_range" not in st.session_state:
                        st.session_state["cohesion_range"] = (round(coh_min, 1), round(coh_max, 1))

                    cohesion_range = st.slider(
                        "Select Cohesion Range",
                        min_value=round(coh_min, 1),
                        max_value=round(coh_max, 1),
                        value=st.session_state["cohesion_range"],
                        key="cohesion_range"
                    )
                else:
                    cohesion_range = None

                st.markdown("### Angle of Internal Friction (°)")
                if "Angle of internal friction (degree)" in simulant_db_df.columns:
                    ang_min, ang_max = float(simulant_db_df["min_Angle of internal friction (degree)"].min(skipna=True)), float(simulant_db_df["max_Angle of internal friction (degree)"].max(skipna=True))

                    if "angle_range" not in st.session_state:
                        st.session_state["angle_range"] = (round(ang_min, 1), round(ang_max, 1))

                    angle_range = st.slider( 
                        "Select Angle Range",
                        min_value=round(ang_min, 1),
                        max_value=round(ang_max, 1),
                        value=st.session_state["angle_range"],
                        key="angle_range"
                        )
                else:
                    angle_range = None

            with st.expander("Select Table Columns", expanded=False):
                # --- Column Selection ---
                st.divider()
                st.header("Display Options")
                all_columns = simulant_db_df.columns.tolist()
                default_columns = ["Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)", "Source","Year of publication","DOI / URL"]
                def select_all_simulant_columns():
                    st.session_state["simulant_selected_columns"] = all_columns

                def clear_simulant_columns():
                    st.session_state["simulant_selected_columns"] = default_columns

                col_select_all, col_clear_selection = st.columns([1, 1])

                with col_select_all:
                    st.button(
                        "Select All Parameters", 
                        on_click=select_all_simulant_columns, 
                        use_container_width=True
                    )

                with col_clear_selection:
                     st.button(
                        "Clear Selection", 
                        on_click=clear_simulant_columns, 
                        use_container_width=True
                )

                selected_columns = st.multiselect(
                    "Select columns to display:",
                    options=all_columns,
                    default=[col for col in default_columns if col in all_columns],
                    key = "simulant_selected_columns"
                )
                
            
            st.button("Clear all filters", use_container_width=True, on_click=clear_all_filters)

    filtered_db_df = simulant_db_df.copy()
    if soil_group_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Soil Group"].isin(soil_group_filter)]
    if test_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Test"].isin(test_filter)]
    if agency_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Agency"].isin(agency_filter)]
    if developer_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Developer"].isin(developer_filter)]
    if year_range and isinstance(year_range, tuple) and (year_range != (year_min, year_max)):
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Year of publication"] >= year_range[0]) &
            (filtered_db_df["Year of publication"] <= year_range[1])
        ]


        # --- Numeric filters  ---
    if density_range:
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Bulk density (g/cm^3)", "max_Bulk density (g/cm^3)",
            density_range[0], density_range[1]
        )
    
    if cohesion_range:
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Cohesion (kPa)", "max_Cohesion (kPa)",
            cohesion_range[0], cohesion_range[1]
        )
    
    if angle_range:
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Angle of internal friction (degree)", "max_Angle of internal friction (degree)",
            angle_range[0], angle_range[1]
        )
    
    # --- Prepare display dataframe with ranges as original strings ---
    display_df = filtered_db_df.copy()

    numeric_range_cols = [
    "Bulk density (g/cm^3)",
    "Angle of internal friction (degree)",
    "Cohesion (kPa)",
    ]

    for col in range_columns:
        # Keep _min, _max, _avg numeric, only replace the original column for display
        if col in display_df.columns:
            display_df[col] = simulant_db_df.loc[display_df.index, col]

    # --- Display filtered table ---
    st.subheader("Database Table")
    if selected_columns:
        st.dataframe(display_df[selected_columns])
    else:
        st.info("No columns selected. Please select at least one column to display.")


    # Plotting Section & Display
    st.subheader("Plot Numerical Data")
    x_axis = st.selectbox("X-axis (categorical & numeric)", [
        "Developer", "Agency", "Simulant", "Year", "Test", "Type of simulant",  
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)"
    ])
    y_axis = st.selectbox("Y-axis (numeric)", [
        "Bulk density (g/cm^3)", "Angle of internal friction (degree)", "Cohesion (kPa)"
    ])

    plot_mode = st.radio("Select value type to plot", ["Range", "Average", "Minimum", "Maximum"], horizontal=True)

    legend_column = st.selectbox("Select Legend", options=[
    "Agency", 
    "Type of simulant", 
    "Test", 
    ], index=0)
       

    # Apply to lunar dataset once
    for col in range_columns:
        if col in simulant_db_df.columns:
            simulant_db_df[[f"min_{col}", f"max_{col}"]] = simulant_db_df[col].apply(
            lambda x: pd.Series(extract_range(x))
            )
            simulant_db_df[f"avg_{col}"] = simulant_db_df[
                [f"min_{col}", f"max_{col}"]
            ].mean(axis=1)

    for col in range_columns:
        if f"min_{col}" in simulant_db_df.columns:
            simulant_db_df[f"min_{col}"] = pd.to_numeric(simulant_db_df[f"min_{col}"], errors="coerce")
            simulant_db_df[f"max_{col}"] = pd.to_numeric(simulant_db_df[f"max_{col}"], errors="coerce")

    # --- Apply filters ---
    filtered_plot_df = simulant_db_df.copy()
    filtered_plot_df["Year of publication"] = pd.to_numeric(filtered_plot_df["Year of publication"], errors="coerce")

    if test_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Test"].isin(test_filter)]
    if soil_group_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Type of simulant"].isin(soil_group_filter)]
    if agency_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Agency"].isin(agency_filter)]
    if developer_filter:
        filtered_plot_df = filtered_plot_df[filtered_plot_df["Developer"].isin(developer_filter)]


    
    if year_range and isinstance(year_range, tuple) and (year_range != (year_min, year_max)):
        filtered_plot_df = filtered_plot_df[
            (filtered_plot_df["Year of publication"] >= year_range[0]) &
            (filtered_plot_df["Year of publication"] <= year_range[1])
        ]


    if density_range and (density_range != (round(dens_min, 2), round(dens_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Bulk density (g/cm^3)", "max_Bulk density (g/cm^3)",
            density_range[0], density_range[1]
        )

    if cohesion_range and (cohesion_range != (round(coh_min, 2), round(coh_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Cohesion (kPa)", "max_Cohesion (kPa)",
            cohesion_range[0], cohesion_range[1]
        )

    if angle_range and (angle_range != (round(ang_min, 2), round(ang_max, 2))):
        filtered_plot_df = filter_numeric_range(
            filtered_plot_df,
            "min_Angle of internal friction (degree)", "max_Angle of internal friction (degree)",
            angle_range[0], angle_range[1]
        )


    # Define colors and markers

    def get_plot_maps(column):
    # Base colors/shapes for mission group

        if column == "Type of simulant":
            return {"Mare": "#1f77b4", "Highland": "#ff7f0e", "Pyroclastic deposit": "#2ca02c", "Other": "gray"}, {"Mare": "circle", "Highland": "square", "Pyroclastic deposit": "diamond", "Other": "cross"}

        if column == "Agency":
            return {"ESA": "#1f77b4", "NASA": "#ff7f0e", "CNSA": "#2ca02c", "KASA": "#9467bd", "ISRO": "#8c564b", "JAXA": "#d62728", "GISTDA": "#e377c2", "Other": "gray" }, {"ESA": "circle", "NASA": "square", "CNSA": "diamond", "KASA": "triangle-up", "ISRO": "triangle-down", "JAXA": "star", "GISTDA": "hexagon", "Other": "x"}
        if column == "Test":
            return {"Direct Shear": "#1f77b4", "Triaxial compression": "#ff7f0e", "Other": "#2ca02c"}, {"Direct Shear": "circle", "Triaxial compression": "square", "Other": "diamond"}
        
        return {"Mare": "#1f77b4", "Highland": "#ff7f0e", "Pyroclastic deposit": "#2ca02c", "Other": "gray"}, {"Mare": "circle", "Highland": "square", "Pyroclastic deposit": "diamond", "Other": "cross"}

    color_map, marker_shapes = get_plot_maps(legend_column)

    # --- Determine Y columns ---
    y_min_col = f"min_{y_axis}"
    y_max_col = f"max_{y_axis}"
    y_col_map = {
        "Average": f"avg_{y_axis}",
        "Minimum": y_min_col,
        "Maximum": y_max_col,
        "Range": y_axis
    }
    y_col_name = y_col_map[plot_mode]

    # Check if x-axis is numeric (one of the measurement columns)
    x_axis_is_numeric = x_axis in range_columns

    # Remove rows with missing Y data
    if plot_mode == "Range":
        filtered_plot_df = filtered_plot_df.dropna(subset=[y_min_col, y_max_col])
        if x_axis_is_numeric:
            # Also need x-axis range columns
            x_min_col = f"min_{x_axis}"
            x_max_col = f"max_{x_axis}"
            filtered_plot_df = filtered_plot_df.dropna(subset=[x_min_col, x_max_col])
    else:
        filtered_plot_df = filtered_plot_df.dropna(subset=[y_col_name])


     # --- RANGE MODE PLOTTING ---
    if plot_mode == "Range":
        fig = go.Figure()

        # For categorical x-axis, create position mapping
        if not x_axis_is_numeric:
            x_categories = filtered_plot_df[x_axis].dropna().unique()
            x_positions = {val: idx for idx, val in enumerate(x_categories)}

        legend_groups = set()

        if color_map is None:
            color_map = {}
            unique_groups = filtered_plot_df[legend_column].dropna().unique()
            default_colors = px.colors.qualitative.Plotly
            for i, group in enumerate(unique_groups):
                color_map[group] = default_colors[i % len(default_colors)]

        for _, row in filtered_plot_df.iterrows():
            group = row[legend_column]
            color = color_map.get(group, "gray")

            # --- Handle X-axis positioning ---
            if x_axis_is_numeric:
                # X-axis is numeric: use actual range values
                x_min_col = f"min_{x_axis}"
                x_max_col = f"max_{x_axis}"
                x_min = row[x_min_col]
                x_max = row[x_max_col]

                if pd.isna(x_min) or pd.isna(x_max):
                    continue
                
                x_display = f"{x_min:.2f}–{x_max:.2f}"
            else:
                # X-axis is categorical: use position with small width
                x_val = row[x_axis]
                if pd.isna(x_val) or x_val not in x_positions:
                    continue
                
                x_pos = x_positions[x_val]
                x_min = x_pos - 0.35
                x_max = x_pos + 0.35
                x_display = str(x_val)

            # --- Handle Y-axis range ---
            y_min = row[y_min_col]
            y_max = row[y_max_col]

            if pd.isna(y_min) or pd.isna(y_max):
                continue
            
            # Rectangle coordinates
            x_coords = [x_min, x_max, x_max, x_min, x_min]
            y_coords = [y_min, y_min, y_max, y_max, y_min]

            # --- Draw filled rectangle ---
            show_legend = group not in legend_groups
            legend_groups.add(group)

            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                fill="toself",
                fillcolor=color,
                line=dict(color=color, width=2),
                opacity=0.5,
                name=group,
                legendgroup=group,
                showlegend=show_legend,
                hoverinfo="text",
                hovertext=(
                    f"Simulant: {row['Simulant']}<br>"
                    f"{x_axis}: {x_display}<br>"
                    f"{y_axis}: {y_min:.2f}–{y_max:.2f}<br>"
                    f"Group: {group}"
                )
            ))

        # --- Update layout based on x-axis type ---
        if x_axis_is_numeric:
            fig.update_layout(
                xaxis=dict(
                    title=x_axis,
                    type="linear",
                    tickformat=".2f"
                )
            )
        else:
            fig.update_layout(
                xaxis=dict(
                    title=x_axis,
                    tickmode="array",
                    tickvals=list(range(len(x_categories))),
                    ticktext=list(x_categories)
                )
            )

        fig.update_layout(
            title=f"{y_axis} Range vs {x_axis}",
            yaxis=dict(title=y_axis, tickformat=".2f"),
            height=600,
            width=800,
            hovermode="closest",
            legend_title_text=legend_column,
        )


    # --- SCATTER PLOT MODES (Average, Min, Max) ---
    else:
        fig = px.scatter(
            filtered_plot_df,
            x=x_axis,
            y=y_col_name,
            color=legend_column,
            symbol=legend_column,
            color_discrete_map=color_map,
            symbol_map=marker_shapes,
            hover_data={"Simulant": True, x_axis: True, y_col_name: ":.2f", legend_column: True},
            title=f"{plot_mode} {y_axis} vs {x_axis}",
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        fig.update_layout(
            xaxis_title=x_axis,
            yaxis_title=f"{y_axis} ({plot_mode})",
            hoverlabel=dict(bgcolor="white", font_size=12, font_color="black"),
            title=dict(x=0, xanchor='left', font=dict(size=20)),
            legend_title_text=legend_column,
            width=800,
            height=500,
        )
     # --- Display plot ---
    config = {"displayModeBar": False, "scrollZoom": True}
        # Watermark
    add_watermark(fig)
    st.plotly_chart(fig, width='stretch', config=config)






#----------------------------------------------------------------------------------------------------------------------------------
#-------- Lunar Samples Section --------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------
elif db_choice == "Lunar Samples Database":

    st.title("Lunar Samples Database")

    samples_PSD_db_df.columns = samples_PSD_db_df.columns.str.strip()
    samples_db_df.columns = samples_db_df.columns.str.strip()

    # Add mission data from regolith dataset
    mission_meta_df = lunar_db_df[["Mission", "Location", "Terrain", "Year", "Type of mission"]].dropna(subset=["Mission"]).drop_duplicates(subset=["Mission"])

    samples_db_df = samples_db_df.merge(mission_meta_df, on="Mission", how="left")
    samples_PSD_db_df = samples_PSD_db_df.merge(mission_meta_df, on="Mission", how="left")


    # --- Columns that contain ranges ---
    range_columns = [ "depth (cm)" ]

    samples_PSD_db_df.columns = samples_PSD_db_df.columns.str.strip()

    # --- Numeric columns ---
    for col in range_columns:
        if col in samples_PSD_db_df.columns:
            samples_PSD_db_df[[f"min_{col}", f"max_{col}"]] = samples_PSD_db_df[col].apply(
                lambda x: pd.Series(extract_range(x))
            )
            samples_PSD_db_df[f"avg_{col}"] = samples_PSD_db_df[
                [f"min_{col}", f"max_{col}"]
            ].mean(axis=1)

    samples_db_df["Mission Group"] = samples_db_df["Mission"].apply(categorize_mission)
    samples_PSD_db_df["Mission Group"] = samples_PSD_db_df["Mission"].apply(categorize_mission)

    numeric_cols = ["Sample", "Sieve size (µm)", "weight %", "weight (g)"]
    for col in numeric_cols:
        if col in samples_PSD_db_df.columns:
            samples_PSD_db_df[col] = pd.to_numeric(samples_PSD_db_df[col], errors="coerce")
        if col in samples_db_df.columns:
            samples_db_df[col] = pd.to_numeric(samples_db_df[col], errors="coerce")


# ------- Filters ----------------------
    st.sidebar.header("Filter Samples Data")
    
    # Mission Filter
    missions = samples_PSD_db_df["Mission"].dropna().unique().tolist()
    selected_missions = st.sidebar.multiselect("Select Mission(s):", options=missions)

    if selected_missions:
        filtered_psd_df = samples_PSD_db_df[samples_PSD_db_df["Mission"].isin(selected_missions)]
        filtered_samples_df = samples_db_df[samples_db_df["Mission"].isin(selected_missions)]
    else:
        filtered_psd_df = samples_PSD_db_df.copy()
        filtered_samples_df = samples_db_df.copy()

    # Sample Filter 
    samples = filtered_psd_df["Sample"].dropna().unique().tolist()
    selected_samples = st.sidebar.multiselect("Select Sample(s):", options=samples)

    if selected_samples:
        filtered_psd_df = filtered_psd_df[filtered_psd_df["Sample"].isin(selected_samples)]
        filtered_samples_df = filtered_samples_df[filtered_samples_df["Sample"].isin(selected_samples)]

    if "Subsample" in filtered_psd_df.columns:
        subsamples = filtered_psd_df["Subsample"].dropna().unique().tolist()
        selected_subsamples = st.sidebar.multiselect("Select Subsample(s):", options=subsamples)
        if selected_subsamples:
            filtered_psd_df = filtered_psd_df[filtered_psd_df["Subsample"].isin(selected_subsamples)]

    # Terrain Filter
    if "Terrain" in filtered_psd_df.columns:
        terrains = filtered_psd_df["Terrain"].dropna().unique().tolist()
        selected_terrains = st.sidebar.multiselect("Select Terrain(s):", options=terrains)

        if selected_terrains:
            filtered_psd_df = filtered_psd_df[filtered_psd_df["Terrain"].isin(selected_terrains)]
            if "Terrain" in filtered_samples_df.columns:
                filtered_samples_df = filtered_samples_df[filtered_samples_df["Terrain"].isin(selected_terrains)]

    # Depth Slider 
    if "min_depth (cm)" in filtered_psd_df.columns and not filtered_psd_df["min_depth (cm)"].dropna().empty:
        min_limit = float(filtered_psd_df["min_depth (cm)"].min())
        max_limit = float(filtered_psd_df["max_depth (cm)"].max())

        st.sidebar.markdown("---")
        depth_range = st.sidebar.slider(
            "Select Depth Range (cm):",
            min_value=min_limit,
            max_value=max_limit,
            value=(min_limit, max_limit)
        )

        if depth_range[0] > min_limit or depth_range[1] < max_limit:
            filtered_psd_df = filtered_psd_df[
                (filtered_psd_df["min_depth (cm)"] >= depth_range[0]) & 
                (filtered_psd_df["max_depth (cm)"] <= depth_range[1])
            ]

            remaining_samples = filtered_psd_df["Sample"].unique()
            if "Sample" in filtered_samples_df.columns:
                filtered_samples_df = filtered_samples_df[filtered_samples_df["Sample"].isin(remaining_samples)]


    st.subheader("Lunar Samples")
    st.dataframe(filtered_samples_df)

    st.subheader("Particle Size Distribution Data")

    summary_cols = ["Mission", "Sample", "Subsample", "depth (cm)", "D50 (µm)","Source"]
    
    existing_summary_cols = [c for c in summary_cols if c in filtered_psd_df.columns]
    
    psd_summary_df = filtered_psd_df[existing_summary_cols].drop_duplicates(subset=["Subsample"])
    
    st.dataframe(psd_summary_df)
    st.info("Select subsamples in the plotting section to view particle size distribution details and plots.")

 #- ---- PSD plotting ------------

    st.write("---")
    st.subheader("Plot Samples Data")
    
    plot_mode = st.radio("Select Analysis Type:", ["Cumulative PSD Curve", "Parameter Scatter Plot"], horizontal=True)

    if plot_mode == "Cumulative PSD Curve":
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1:
            legend_color = st.selectbox(
                "Color Legend (Primary):", 
                options=["Subsample", "Mission", "Terrain", "Type of mission", "depth (cm)", "D50 (µm)"], 
                index=0
            )
        with col_leg2:
            legend_dash = st.selectbox(
                "Line Style Legend (Secondary):", 
                options=["None", "Mission", "Terrain", "Sample", "depth (cm)"], 
                index=0
            )

        st.markdown("**Refine PSD Curve Data:**")
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            available_samples = filtered_psd_df["Sample"].dropna().unique().tolist()
            local_sample_filter = st.multiselect(
                "Isolate Specific Sample(s):", 
                options=available_samples,
                help="Select one or more parent samples."
            )
            
        with filter_col2:
            if local_sample_filter:
                sub_options = filtered_psd_df[filtered_psd_df["Sample"].isin(local_sample_filter)]["Subsample"].dropna().unique().tolist()
            else:
                sub_options = filtered_psd_df["Subsample"].dropna().unique().tolist()
                
            local_subsample_filter = st.multiselect(
                "Isolate Specific Subsample(s):", 
                options=sub_options,
                help="Select specific depth slices."
            )

        if not local_sample_filter and not local_subsample_filter:
            st.info("Please select at least one Sample or Subsample above to generate the PSD plot.")
        else:
            sub_df = filtered_psd_df.copy()
            if local_sample_filter:
                sub_df = sub_df[sub_df["Sample"].isin(local_sample_filter)]
            if local_subsample_filter:
                sub_df = sub_df[sub_df["Subsample"].isin(local_subsample_filter)]

            selected_count = len(sub_df["Subsample"].unique())
            st.caption(f"Plotting **{selected_count}** specific subsample(s).")

            # Plotting
            if not sub_df.empty:
                sub_df = sub_df.sort_values(by=["Subsample", "Sieve size (µm)"], ascending=[True, False])
                sub_df["Cumulative Weight %"] = sub_df.groupby("Subsample")["weight %"].transform(pd.Series.cumsum)

                dash_val = legend_dash if legend_dash != "None" else None

                fig = px.line(
                    sub_df, 
                    x="Sieve size (µm)", 
                    y="Cumulative Weight %", 
                    color=legend_color,
                    line_dash=dash_val,
                    line_group="Subsample", 
                    markers=True, 
                    log_x=True,
                    title="Comparative PSD: Multi-Variable Legend",
                    hover_data=["Subsample", "Mission", "depth (cm)"]
                )

                fig.update_xaxes(autorange="reversed")
                    # Watermark
                add_watermark(fig)
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("🔍 View Calculation Details"):
                    st.write("Below is the cumulative breakdown for the selected samples:")
                    details_df = sub_df.pivot_table(
                        index="Sieve size (µm)", 
                        columns="Subsample", 
                        values="Cumulative Weight %"
                    ).sort_index(ascending=False)
                    
                    st.dataframe(details_df, use_container_width=True)
                    st.info("💡 Values represent the Cumulative Weight Retained (%) for each sieve size.")
            else:
                st.warning("No data available to plot based on the current filters.")

    # Scatter plot
    else:
        col1, col2 = st.columns(2)
        axis_options = {"Average Depth (cm)": "avg_depth (cm)", "D50 (µm)": "D50 (µm)"}
        
        with col1:
            x_label = st.selectbox("X-Axis:", options=list(axis_options.keys()), index=0)
        with col2:
            y_label = st.selectbox("Y-Axis:", options=list(axis_options.keys()), index=1)
        
        color_by = st.selectbox(
            "Color Points By:", 
            options=["Mission", "Terrain", "Type of mission", "Sample", "Subsample"],
            index=1 
        )

        st.markdown("**Refine Scatter Plot Data:**")
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            available_samples = filtered_psd_df["Sample"].dropna().unique().tolist()
            local_sample_filter = st.multiselect(
                "Isolate Specific Sample(s):", 
                options=available_samples,
                help="Leave blank to plot all samples currently active in the sidebar."
            )
            
        with filter_col2:
            if local_sample_filter:
                sub_options = filtered_psd_df[filtered_psd_df["Sample"].isin(local_sample_filter)]["Subsample"].dropna().unique().tolist()
            else:
                sub_options = filtered_psd_df["Subsample"].dropna().unique().tolist()
                
            local_subsample_filter = st.multiselect(
                "Isolate Specific Subsample(s):", 
                options=sub_options,
                help="Leave blank to plot all available subsamples."
            )

        scatter_df = filtered_psd_df.drop_duplicates(subset=["Subsample"]).copy()

        if local_sample_filter:
            scatter_df = scatter_df[scatter_df["Sample"].isin(local_sample_filter)]
        if local_subsample_filter:
            scatter_df = scatter_df[scatter_df["Subsample"].isin(local_subsample_filter)]

        if not local_sample_filter and not local_subsample_filter:
            st.caption("Currently plotting **ALL** data selected in the global sidebar.")
        else:
            st.caption(f"Plotting **{len(scatter_df)}** specific subsample(s).")

        # --- Plotting ---
        fig = px.scatter(
            scatter_df, 
            x=axis_options[x_label], 
            y=axis_options[y_label], 
            color=color_by,
            hover_data=["Subsample", "depth (cm)", "Terrain", "Location", "Year"],
            labels={axis_options[x_label]: x_label, axis_options[y_label]: y_label},
            title=f"{y_label} vs {x_label}"
        )
        
        if axis_options[y_label] == "avg_depth (cm)":
            fig.update_yaxes(autorange="reversed")
        
            # Watermark
        add_watermark(fig)
        st.plotly_chart(fig, use_container_width=True)


#------------------ Detailed Mission Pages Section ---------------------------
elif db_choice == "Detailed Mission Pages":
    st.title("Detailed Lunar Mission Pages")

    BASE_DIR = Path(__file__).resolve().parent
    MISSION_DIR = BASE_DIR / "mission_pages"

    if not MISSION_DIR.exists():
        st.error(f"Could not find mission directory: {MISSION_DIR}")
    else:
        # 1. Categorize missions into groups
        mission_groups = {
            "Apollo": {},
            "Luna": {},
            "Surveyor": {},
            "Chang'e": {},
            "Chandrayaan": {},
            "Other": {}
        }

        for path in MISSION_DIR.glob("*.py"):
            if path.name.startswith("__"): continue
            
            raw_name = path.stem.lower()
            mission_name = pretty_mission_name(raw_name) # Assuming this helper exists
            
            if mission_name in ["Mission Page Template", "Mission"]: continue

            # Sort into the correct dictionary key
            if "apollo" in raw_name:
                mission_groups["Apollo"][mission_name] = path
            elif "luna" in raw_name:
                mission_groups["Luna"][mission_name] = path
            elif "surveyor" in raw_name:
                mission_groups["Surveyor"][mission_name] = path
            elif "chang" in raw_name:
                mission_groups["Chang'e"][mission_name] = path
            elif "chandrayaan" in raw_name:
                mission_groups["Chandrayaan"][mission_name] = path
            else:
                mission_groups["Other"][mission_name] = path

        # 2. Main Page Selection UI
        st.write("### Explore Mission Data")
        
        # Create two columns for a clean look
        col1, col2 = st.columns(2)
        
        with col1:
            group_choice = st.selectbox(
                "Select a Space Program:",
                options=list(mission_groups.keys())
            )

        with col2:
            # Filter specific missions based on the group choice
            specific_missions = mission_groups[group_choice]
            mission_choice = st.selectbox(
                "Select a Specific Mission:",
                options=[""] + sorted(specific_missions.keys()),
                format_func=lambda x: f"Select {group_choice} mission..." if x == "" else x
            )

        # 3. Load and display selected mission page
        if mission_choice:
            st.divider()
            mission_file = specific_missions[mission_choice]

            module_name = f"mission_{mission_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, mission_file)
            mission_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mission_module)
            
            if hasattr(mission_module, "show_mission"):
                mission_module.show_mission(lunar_db_df)
            else:
                st.warning("No show_mission() function found.")
        else:
            st.info("Please select a specific mission from the dropdown menus above.")





# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## --------------------------- All Data Section ---------------------------
elif db_choice == "Combined Data":
    st.title("Combined Dataset")

    all_db_df.columns = all_db_df.columns.str.strip()
    numeric_cols = ["Year", "Year of publication"]
    for col in numeric_cols:
        if col in all_db_df.columns:
            all_db_df[col] = pd.to_numeric(all_db_df[col], errors="coerce")

    def categorize_mission(mission_name):
        if pd.isna(mission_name):
            return "Other"
        name = mission_name.lower()
        if "apollo" in name:
            return "Apollo"
        elif "orbiter" in name:
            return "LRO"
        elif "luna" in name:
            return "Luna"
        elif "surveyor" in name:
            return "Surveyor"
        elif "chang'e" in name:
            return "Chang'e"
        elif "chandrayaan" in name: 
            return "Chandrayaan"
        else:
            return "Simulant"
        
    def categorize_soil(soil_name):
        if pd.isna(soil_name):
            return "Other"
        name = soil_name.lower()
        if "mare" in name:
            return "Mare"
        elif "highland" in name:
            return "Highland"
        elif "pyroclastic" in name:
            return "Pyroclastic deposit"
        else:
            return "Other"
    
    def extract_range(value):
        if pd.isna(value):
            return (np.nan, np.nan)
        
        if isinstance(value, (int, float)):
            return (float(value), float(value))

        match = re.findall(r"[-+]?\d*\.?\d+", str(value))

        if len(match) == 0:
            return (np.nan, np.nan)

        try:
            numbers = [float(n) for n in match]
        except ValueError:
            return (np.nan, np.nan)

        if len(numbers) == 1:
            val = numbers[0]
            return (val, val)
        else:
            return (min(numbers), max(numbers))

    # --- Columns that may contain ranges ---
    range_columns = [
        "Bulk density (g/cm^3)",
        "Angle of internal friction (degree)",
        "Cohesion (kPa)",
        "Bearing capacity (kPa)", 
        "Normal stress range (kPa)", 
        "Void ratio", 
        "Density of grains (g/cm^3)", 
        "Compressibility Coefficient", 
        "Depth (cm)", 
        "Porosity (%)", 
        "Force applied (N)"
    ]

    # --- Numeric columns ---
    for col in range_columns:
        if col in all_db_df.columns:
            all_db_df[[f"min_{col}", f"max_{col}"]] = all_db_df[col].apply(
                lambda x: pd.Series(extract_range(x))
            )
            all_db_df[f"avg_{col}"] = all_db_df[
                [f"min_{col}", f"max_{col}"]
            ].mean(axis=1)

    all_db_df["Mission Group"] = all_db_df["Mission / Simulant"].apply(categorize_mission)
    all_db_df["Soil Group"] = all_db_df["Terrain"].apply(categorize_soil)

    # Sidebar Filters
    def clear_all_filters():
        st.session_state["soil_group_filter"] = []
        st.session_state["test_filter"] = []
        st.session_state["mission_type_filter"] = []
        st.session_state["mission_group_filter"] = []
        st.session_state["test_location_filter"] = []
        st.session_state["agency_filter"] = []
        st.session_state["developer_filter"] = []
        st.session_state["year_range"] = (year_min, year_max)
        st.session_state["density_range"] = (round(dens_min, 2), round(dens_max, 2))
        st.session_state["cohesion_range"] = (round(coh_min, 1), round(coh_max, 1))
        st.session_state["angle_range"] = (round(ang_min, 1), round(ang_max, 1))
        st.session_state["sbc_range"] = (round(sbc_min, 1), round(sbc_max, 1))
        st.session_state["ns_range"] = (round(nf_min, 1), round(nf_max, 1))
        st.session_state["vr_range"] = (round(vr_min, 2), round(vr_max, 2))
        st.session_state["dg_range"] = (round(dg_min, 2), round(dg_max, 2))
        st.session_state["cc_range"] = (round(cc_min, 4), round(cc_max, 4))
        st.session_state["depth_range"] = (round(depth_min, 1), round(depth_max, 1))
        st.session_state["por_range"] = (round(por_min, 1), round(por_max, 1))
        st.session_state["fa_range"] = (round(fa_min, 1), round(fa_max, 1))
        st.session_state["selected_columns"] = [
            col for col in default_columns if col in lunar_db_df.columns
        ]

    with st.sidebar:
        st.header("Filter Data")
        with st.expander("Categorical Filters", expanded=False):
            st.markdown("### Terrain")
            soil_options = all_db_df["Terrain"].dropna().astype(str).unique()
            soil_group_filter = st.multiselect("Select Terrain type", options=sorted(soil_options), key="soil_group_filter")
            #soil_group_filter = st.multiselect("Select Terrain type", options=sorted(all_db_df["Soil Group"].dropna().unique()), key="soil_group_filter")
            st.markdown("### Test Type")
            test_filter = st.multiselect("Select Test Type", options=sorted(all_db_df["Test"].dropna().unique()), key="test_filter")
            st.markdown("### Agency")
            agency_filter = st.multiselect("Select Agency", ["NASA", "ESA", "JAXA", "KASA", "ISRO", "CNSA", "GISTDA"], key="agency_filter")
            st.markdown("### Developer")
            developer_filter = st.multiselect("Select Developer(s):", options=sorted(all_db_df["Developer"].dropna().unique()), key="developer_filter")
            st.markdown("### Type of Mission")
            mission_type_filter = st.multiselect(
                "Select type of mission:",
                options=sorted(all_db_df["Type of mission"].dropna().unique()),
                key="mission_type_filter"
            )

            st.markdown("### Mission Group")
            mission_group_filter = st.multiselect(
                "Select Mission Group", 
                options=["Apollo", "Luna", "Surveyor", "Chang'e", "Chandrayaan", "Lunar Reconnaissance Orbiter", "Other"],
                key="mission_group_filter"
            )

            st.markdown("### Test Location")
            test_location_filter = st.multiselect(
                "Select Test Location", 
                options=["In-Situ", "On Earth", "Remote", "Other"],
                key="test_location_filter"
            )

            # --- Numeric Range Filters ---
        with st.expander("Numeric Range Filters", expanded=False):
            year_range = None
            year_min = None 
            year_max = None
            st.markdown("### Publication Year")
            if "Year of publication" in all_db_df.columns:
                numeric_years = pd.to_numeric(all_db_df["Year of publication"], errors="coerce")
                year_min = int(numeric_years.min(skipna=True))
                year_max = int(numeric_years.max(skipna=True))

                if "year_range" not in st.session_state:
                    st.session_state["year_range"] = (year_min, year_max)

                year_range = st.slider(
                    "Select Year of publication Range",
                    min_value=year_min,
                    max_value=year_max,
                    key="year_range"
                )
            else:
                year_range = None


            st.markdown("### Bulk Density (g/cm³)")
            if "min_Bulk density (g/cm^3)" in all_db_df.columns:
                dens_min = float(all_db_df["min_Bulk density (g/cm^3)"].min(skipna=True))
                dens_max = float(all_db_df["max_Bulk density (g/cm^3)"].max(skipna=True))

                if "density_range" not in st.session_state:
                    st.session_state["density_range"] = (round(dens_min, 2), round(dens_max, 2))    

                density_range = st.slider(
                    "Select Density Range",
                    min_value=round(dens_min, 2),
                    max_value=round(dens_max, 2),
                    value=(round(dens_min, 2), round(dens_max, 2)),
                    key="density_range"
                )
            else:
                density_range = None

            st.markdown("### Cohesion (kPa)")
            if "min_Cohesion (kPa)" in all_db_df.columns:
                coh_min = float(all_db_df["min_Cohesion (kPa)"].min(skipna=True))
                coh_max = float(all_db_df["max_Cohesion (kPa)"].max(skipna=True))

                if "cohesion_range" not in st.session_state:
                    st.session_state["cohesion_range"] = (round(coh_min, 1), round(coh_max, 1))

                cohesion_range = st.slider(
                    "Select Cohesion Range",
                    min_value=round(coh_min, 1),
                    max_value=round(coh_max, 1),
                    value=(round(coh_min, 1), round(coh_max, 1)),
                    key="cohesion_range"
                )
            else:
                cohesion_range = None

            st.markdown("### Angle of Internal Friction (°)")
            if "min_Angle of internal friction (degree)" in all_db_df.columns:
                ang_min = float(all_db_df["min_Angle of internal friction (degree)"].min(skipna=True))
                ang_max = float(all_db_df["max_Angle of internal friction (degree)"].max(skipna=True))

                if "angle_range" not in st.session_state:
                    st.session_state["angle_range"] = (round(ang_min, 1), round(ang_max, 1))

                angle_range = st.slider(
                    "Select Angle Range",
                    min_value=round(ang_min, 1),
                    max_value=round(ang_max, 1),
                    value=(round(ang_min, 1), round(ang_max, 1)),
                    key="angle_range"
                )
            else:
                angle_range = None

            st.markdown("### Bearing Capacity (kPa)")
            if "min_Bearing capacity (kPa)" in all_db_df.columns:
                sbc_min = float(all_db_df["min_Bearing capacity (kPa)"].min(skipna=True))
                sbc_max = float(all_db_df["max_Bearing capacity (kPa)"].max(skipna=True))

                if "sbc_range" not in st.session_state:
                    st.session_state["sbc_range"] = (round(sbc_min, 1), round(sbc_max, 1))

                sbc_range = st.slider(
                   "Select Bearing Capacity Range",
                   min_value=round(sbc_min, 1),
                   max_value=round(sbc_max, 1),
                   value=(round(sbc_min, 1), round(sbc_max, 1)),
                   key="sbc_range"
               )
            else:
                sbc_range = None

            st.markdown("### Normal Stress (kPa)")
            if "min_Normal stress range (kPa)" in all_db_df.columns:
                nf_min = float(all_db_df["min_Normal stress range (kPa)"].min(skipna=True))
                nf_max = float(all_db_df["max_Normal stress range (kPa)"].max(skipna=True))

                if "ns_range" not in st.session_state:
                    st.session_state["ns_range"] = (round(nf_min, 1), round(nf_max, 1))

                nf_range = st.slider(
                   "Select Normal Stress Range",
                   min_value=round(nf_min, 1),
                   max_value=round(nf_max, 1),
                   value=(round(nf_min, 1), round(nf_max, 1)),
                   key="ns_range"
               )
            else:
                nf_range = None

            st.markdown("### Void Ratio")
            if "min_Void ratio" in all_db_df.columns:
                vr_min = float(all_db_df["min_Void ratio"].min(skipna=True))
                vr_max = float(all_db_df["max_Void ratio"].max(skipna=True))

                if "vr_range" not in st.session_state:
                    st.session_state["vr_range"] = (round(vr_min, 2), round(vr_max, 2))

                vr_range = st.slider(
                   "Select Void Ratio Range",
                   min_value=round(vr_min, 2),
                   max_value=round(vr_max, 2),
                   value=(round(vr_min, 2), round(vr_max, 2)),
                   key="vr_range"
               )
            else:
                vr_range = None

            st.markdown("### Density of Grains (g/cm³)")
            if "min_Density of grains (g/cm^3)" in all_db_df.columns:
                dg_min = float(all_db_df["min_Density of grains (g/cm^3)"].min(skipna=True))
                dg_max = float(all_db_df["max_Density of grains (g/cm^3)"].max(skipna=True))

                if "dg_range" not in st.session_state:
                    st.session_state["dg_range"] = (round(dg_min, 2), round(dg_max, 2))

                dg_range = st.slider(
                   "Select Density of Grains Range",
                   min_value=round(dg_min, 2),
                   max_value=round(dg_max, 2),
                   value=(round(dg_min, 2), round(dg_max, 2)),
                   key="dg_range"
               )
            else:
                dg_range = None

            st.markdown("### Compressibility Coefficient")
            if "min_Compressibility Coefficient" in all_db_df.columns:
                cc_min = float(all_db_df["min_Compressibility Coefficient"].min(skipna=True))
                cc_max = float(all_db_df["max_Compressibility Coefficient"].max(skipna=True))

                if "cc_range" not in st.session_state:
                    st.session_state["cc_range"] = (round(cc_min, 4), round(cc_max, 4))

                cc_range = st.slider(
                   "Select Compressibility Coefficient Range",
                   min_value=round(cc_min, 4),
                   max_value=round(cc_max, 4),
                   value=(round(cc_min, 4), round(cc_max, 4)),
                   key="cc_range"
               )
            else:
                cc_range = None

            st.markdown("### Depth (cm)")
            if "min_Depth (cm)" in all_db_df.columns:
                depth_min = float(all_db_df["min_Depth (cm)"].min(skipna=True))
                depth_max = float(all_db_df["max_Depth (cm)"].max(skipna=True))

                if "depth_range" not in st.session_state:
                    st.session_state["depth_range"] = (round(depth_min, 1), round(depth_max, 1))

                depth_range = st.slider(
                   "Select Depth Range",
                   min_value=round(depth_min, 1),
                   max_value=round(depth_max, 1),
                   value=(round(depth_min, 1), round(depth_max, 1)),
                   key="depth_range"
               )
            else:
                depth_range = None  

            st.markdown("### Porosity (%)")
            if "min_Porosity (%)" in all_db_df.columns:
                por_min = float(all_db_df["min_Porosity (%)"].min(skipna=True))
                por_max = float(all_db_df["max_Porosity (%)"].max(skipna=True))

                if "por_range" not in st.session_state:
                    st.session_state["por_range"] = (round(por_min, 1), round(por_max, 1))

                por_range = st.slider(
                   "Select Porosity Range",
                   min_value=round(por_min, 1),
                   max_value=round(por_max, 1),
                   value=(round(por_min, 1), round(por_max, 1)),
                   key="por_range"
               )
            else:
                por_range = None

            st.markdown("### Force applied (N)")
            if "min_Force applied (N)" in all_db_df.columns:
                fa_min = float(all_db_df["min_Force applied (N)"].min(skipna=True))
                fa_max = float(all_db_df["max_Force applied (N)"].max(skipna=True))

                if "fa_range" not in st.session_state:
                    st.session_state["fa_range"] = (round(fa_min, 1), round(fa_max, 1))

                fa_range = st.slider(
                   "Select Force applied Range",
                   min_value=round(fa_min, 1),
                   max_value=round(fa_max, 1),
                   value=(round(fa_min, 1), round(fa_max, 1)),
                   key="fa_range"
               )
            else:
                fa_range = None
        
        with st.expander("Select Table Columns", expanded=False):
            st.divider()
            st.header("Display Options")
            all_columns = all_db_df.columns.tolist()
            default_columns = [
        "Mission / Simulant", "Developer", "Agency", "Moon Location", "Terrain", "Year","Type of mission","Test", "Test location", 
        "Bulk density (g/cm^3)", 
        "Angle of internal friction (degree)", 
        "Cohesion (kPa)", 
        "Bearing capacity (kPa)", "Depth (cm)", 
        "Source","Year of publication", "DOI / URL", "Comments"]         

            def select_all_columns():
                st.session_state["selected_columns"] = all_columns

            def clear_columns():
                st.session_state["selected_columns"] = default_columns

            col_select_all, col_clear_selection = st.columns([1, 1])

            with col_select_all:
                st.button(
                    "Select All Parameters", 
                    on_click=select_all_columns, 
                    use_container_width=True
                )

            with col_clear_selection:
                 st.button(
                    "Clear Selection", 
                    on_click=clear_columns, 
                    use_container_width=True
                )

            selected_columns = st.multiselect(
                "Select columns to display:",
                options=all_columns,
                default=[col for col in default_columns if col in all_columns],
                key="selected_columns"
            )

        st.button("Clear all filters", use_container_width=True, on_click=clear_all_filters)





    # --- Apply Filters ---
    filtered_db_df = all_db_df.copy()
    numeric_cols = [
    "Year of publication",
    "Bulk density (g/cm^3)",
    "Angle of internal friction (degree)",
    "Cohesion (kPa)",
    "Bearing capacity (kPa)",
    "Normal stress range (kPa)",
    "Void ratio",
    "Density of grains (g/cm^3)",
    "Compressibility Coefficient",
    "Depth (cm)",
    "Porosity (%)",
    "Force applied (N)",
    "Year"
    ]

    for col in numeric_cols:
        if col in filtered_db_df.columns:
            filtered_db_df[col] = pd.to_numeric(filtered_db_df[col], errors="coerce")

    # Terrain type filter
    #if soil_group_filter:
    #    filtered_db_df = filtered_db_df[filtered_db_df["Terrain"].isin(soil_group_filter)]

    if soil_group_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Terrain"].isin(soil_group_filter)]

    if agency_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Agency"].isin(agency_filter)]

    if developer_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Developer"].isin(developer_filter)]

    # Test type filter
    if test_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Test"].isin(test_filter)]

    # Mission group filter (use Mission Group, not Mission)
    if mission_group_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Mission Group"].isin(mission_group_filter)]

    # Mission type filter
    if mission_type_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Type of mission"].isin(mission_type_filter)]

    # Test location filter
    if test_location_filter:
        filtered_db_df = filtered_db_df[filtered_db_df["Test location"].isin(test_location_filter)]

    # Year of publication filter (only if slider active)
    if year_range and isinstance(year_range, tuple) and (year_range != (year_min, year_max)):
        filtered_db_df = filtered_db_df[
            (filtered_db_df["Year of publication"] >= year_range[0]) &
            (filtered_db_df["Year of publication"] <= year_range[1])
        ]


    # --- Numeric filters ---
    def filter_numeric_range(df, col_min, col_max, min_val, max_val):
        return df[
            ((df[col_max].ge(min_val)) | (df[col_max].isna())) &
            ((df[col_min].le(max_val)) | (df[col_min].isna()))
        ]

    if density_range and (density_range != (round(dens_min, 2), round(dens_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Bulk density (g/cm^3)", "max_Bulk density (g/cm^3)",
            density_range[0], density_range[1]
        )


    if cohesion_range and (cohesion_range != (round(coh_min, 2), round(coh_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Cohesion (kPa)", "max_Cohesion (kPa)",
            cohesion_range[0], cohesion_range[1]
        )

    if angle_range and (angle_range != (round(ang_min, 2), round(ang_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Angle of internal friction (degree)", "max_Angle of internal friction (degree)",
            angle_range[0], angle_range[1]
        )

    if sbc_range and (sbc_range != (round(sbc_min, 2), round(sbc_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Bearing capacity (kPa)", "max_Bearing capacity (kPa)",
            sbc_range[0], sbc_range[1]
        )

    if nf_range and (nf_range != (round(nf_min, 2), round(nf_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Normal stress range (kPa)", "max_Normal stress range (kPa)",
            nf_range[0], nf_range[1]
        )

    if vr_range and (vr_range != (round(vr_min, 2), round(vr_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Void ratio", "max_Void ratio",
            vr_range[0], vr_range[1]
        )
    
    if dg_range and (dg_range != (round(dg_min, 2), round(dg_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Density of grains (g/cm^3)", "max_Density of grains (g/cm^3)",
            dg_range[0], dg_range[1]
        )

    if cc_range and (cc_range != (round(cc_min, 4), round(cc_max, 4))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Compressibility Coefficient", "max_Compressibility Coefficient",
            cc_range[0], cc_range[1]
        )
    
    if depth_range and (depth_range != (round(depth_min, 2), round(depth_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Depth (cm)", "max_Depth (cm)",
            depth_range[0], depth_range[1]
        )

    if por_range and (por_range != (round(por_min, 2), round(por_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Porosity (%)", "max_Porosity (%)",
            por_range[0], por_range[1]
        )

    if fa_range and (fa_range != (round(fa_min, 2), round(fa_max, 2))):
        filtered_db_df = filter_numeric_range(
            filtered_db_df,
            "min_Force applied (N)", "max_Force applied (N)",
            fa_range[0], fa_range[1]
        )
    
    # --- Prepare display dataframe with ranges as original strings ---
    display_df = filtered_db_df.copy()

    # List of numeric columns where you want to display original ranges
    numeric_range_cols = [
        "Bulk density (g/cm^3)",
        "Angle of internal friction (degree)",
        "Cohesion (kPa)",
        "Bearing capacity (kPa)",
        "Normal stress range (kPa)",
        "Void ratio",
        "Density of grains (g/cm^3)",
        "Compressibility Coefficient",
        "Depth (cm)",
        "Porosity (%)",
        "Force applied (N)"
    ]

    for col in numeric_range_cols:
        # Keep _min, _max, _avg numeric, only replace the original column for display
        if col in display_df.columns:
            display_df[col] = all_db_df.loc[display_df.index, col]

    # --- Display filtered table ---
    st.subheader("Database Table")
    if selected_columns:
        st.dataframe(display_df[selected_columns])
    else:
        st.info("No columns selected. Please select at least one column to display.")

    st.markdown(
        "<p style='font-size:12px; color:gray;'>* Indicates values estimated for the measurements.</p>",
        unsafe_allow_html=True
    )




# ------------------- Footer --------------------
import requests
import datetime

with st.sidebar:
    st.divider()
    st.write("### Documentation")
    
    # Read the PDF file into memory
    try:
        with open("User Manual.pdf", "rb") as f:
            pdf_data = f.read()
        
        st.download_button(
            label="Download User Manual",
            data=pdf_data,
            file_name="User Manual.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except FileNotFoundError:
        st.error("Manual not found. Please check the repository.")

@st.cache_data(ttl=3600)
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
        return "Unknown"

last_updated = get_last_commit_date()

st.markdown("To suggest additional data implementation, contact us at gasteinerleonie@gmail.com!")

st.markdown(
    f"<hr><p style='font-size:11px; color:gray; text-align:center;'>© 2026 Lunar Regolith Database <br> Contact us at gasteinerleonie@gmail.com <br> Last updated: {last_updated}</p>",
    unsafe_allow_html=True
)

