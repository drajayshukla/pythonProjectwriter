import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.stats import ttest_ind
import numpy as np

# 1. Page Configuration
st.set_page_config(
    page_title="Liver-Bone Axis Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for scientific look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    h1 { color: #2c3e50; }
    h2 { color: #34495e; border-bottom: 2px solid #ccc; padding-bottom: 10px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.title("🦴 Liver-Bone Axis: HR-pQCT Analytics Engine")
st.markdown("**Project:** Microarchitectural Deterioration in MASLD | **Data Source:** `liver_hrpqct_filled.csv`")

# 2. Data Loading Function
@st.cache_data
def load_data():
    # Robust pathing: tries 'data/' folder first, then root
    paths = ['data/liver_hrpqct_filled.csv', 'liver_hrpqct_filled.csv', '../data/liver_hrpqct_filled.csv']
    for path in paths:
        try:
            df = pd.read_csv(path)
            # Calculated Field: BMI (if missing)
            if 'BMI' not in df.columns and 'Weight_kg' in df.columns:
                df['BMI'] = df['Weight_kg'] / ((df['Height_cm'] / 100) ** 2)
            return df
        except FileNotFoundError:
            continue
    return None

df = load_data()

if df is None:
    st.error("❌ **Critical Error:** Data file not found. Please ensure `liver_hrpqct_filled.csv` is in the `data/` directory.")
    st.stop()

# 3. Sidebar Navigation
st.sidebar.title("Analysis Modules")
module = st.sidebar.radio(
    "Select Module:",
    ["📊 Data Overview", "📈 Descriptive Stats", "🧪 Comparative (T-Test)", "📐 Regression Analysis", "