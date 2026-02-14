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

# Custom CSS
st.markdown("""
<style>
    .reportview-container { background: #f0f2f6 }
    h1 { color: #2c3e50; }
    h2 { color: #34495e; border-bottom: 2px solid #ccc; padding-bottom: 10px; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.title("🦴 Liver-Bone Axis: High-Dimensional Analytics")
st.markdown("**Project:** MASLD Microarchitecture | **Data Source:** `liver_hrpqct_filled.csv`")


# 2. Robust Data Loading
@st.cache_data
def load_data():
    paths = [
        'liver_hrpqct_filled.csv',
        'data/liver_hrpqct_filled.csv',
        '../data/liver_hrpqct_filled.csv',
        'MAFLD_HRPQCT/DATA/liver_hrpqct_filled.csv'
    ]
    for path in paths:
        try:
            df = pd.read_csv(path)
            # Calculated BMI if missing
            if 'BMI' not in df.columns and 'Weight_kg' in df.columns:
                df['BMI'] = df['Weight_kg'] / ((df['Height_cm'] / 100) ** 2)
            return df
        except FileNotFoundError:
            continue
    return None


df = load_data()

if df is None:
    st.error("❌ Critical Error: Data file not found. Please upload `liver_hrpqct_filled.csv`.")
    st.stop()


# --- HELPER: Variable Categorization ---
# This helps organize your 100+ variables into drop-down categories
def get_var_category(col_name):
    col_lower = col_name.lower()
    if 'radius' in col_lower: return "📍 Radius (HR-pQCT)"
    if 'tibia' in col_lower: return "📍 Tibia (HR-pQCT)"
    if any(x in col_lower for x in ['dxa', 'tbs', 'frax', 'bmd']): return "🦴 DXA & FRAX"
    if any(x in col_lower for x in
           ['sclerostin', 'igf', 'ctx', 'p1np', 'rankl', 'opg', 'vit', 'pth', 'calcium']): return "🩸 Bone Markers"
    if any(x in col_lower for x in ['alt', 'ast', 'ggt', 'alp', 'albumin', 'bilirubin', 'inr', 'fibroscan', 'child',
                                    'meld']): return "liver 🟢 Liver Profile"
    if any(x in col_lower for x in
           ['age', 'sex', 'weight', 'height', 'bmi', 'smoking', 'alcohol']): return "👤 Demographics"
    return "🔹 Other Clinical"


all_cols = df.columns.tolist()
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

# Organize numeric variables by category for the sidebar/dropdowns
var_groups = {}
for col in num_cols:
    cat = get_var_category(col)
    if cat not in var_groups: var_groups[cat] = []
    var_groups[cat].append(col)

# 3. Sidebar Navigation
st.sidebar.title("Analysis Modules")
module = st.sidebar.radio(
    "Select Module:",
    ["📊 Data Overview", "📈 Descriptive Stats", "🧪 Group Comparisons", "📐 Regression Analysis", "🔥 Correlation Matrix"]
)
st.sidebar.markdown("---")
st.sidebar.metric("Total Variables", len(all_cols))
st.sidebar.metric("Total Patients", len(df))

# --- MODULE 1: DATA OVERVIEW ---
if module == "📊 Data Overview":
    st.header("Dataset Overview")

    st.info(f"Successfully loaded **{len(all_cols)} variables** for **{len(df)} patients**.")

    with st.expander("🔍 View All Variable Names (Click to Expand)", expanded=False):
        st.write(all_cols)

    with st.expander("📄 View Raw Data Table", expanded=True):
        st.dataframe(df.head(10))

# --- MODULE 2: DESCRIPTIVE STATS ---
elif module == "📈 Descriptive Stats":
    st.header("Descriptive Statistics")

    # Category Filter
    st.markdown("##### 1. Select Variable Category")
    selected_cat = st.selectbox("Filter Variables by Type:", list(var_groups.keys()))

    # Specific Variable Select
    cols_in_cat = var_groups[selected_cat]
    selected_vars = st.multiselect(f"Select {selected_cat} Variables:", cols_in_cat, default=cols_in_cat[:3])

    if selected_vars:
        st.subheader("Summary Table")
        st.dataframe(df[selected_vars].describe().T.style.format("{:.2f}"))

        st.subheader("Distribution Plots")
        viz_var = st.selectbox("Select variable to plot:", selected_vars)

        fig, ax = plt.subplots(1, 2, figsize=(12, 4))

        # Histogram
        sns.histplot(df[viz_var], kde=True, color="teal", ax=ax[0])
        ax[0].set_title(f"Histogram: {viz_var}")

        # Boxplot
        sns.boxplot(x=df[viz_var], color="lightblue", ax=ax[1])
        ax[1].set_title(f"Boxplot: {viz_var}")

        st.pyplot(fig)

# --- MODULE 3: COMPARATIVE ANALYSIS ---
elif module == "🧪 Group Comparisons":
    st.header("Hypothesis Testing")

    # 1. Grouping
    group_var = st.selectbox("Group Patients By:", cat_cols,
                             index=cat_cols.index('Study_Group') if 'Study_Group' in cat_cols else 0)
    unique_groups = df[group_var].dropna().unique()

    c1, c2 = st.columns(2)
    g1 = c1.selectbox("Group 1 (Control):", unique_groups, index=0)
    g2 = c2.selectbox("Group 2 (Test):", unique_groups, index=1 if len(unique_groups) > 1 else 0)

    # 2. Target Variable (Categorized)
    st.markdown("---")
    st.markdown("##### Select Dependent Variable")
    target_cat = st.selectbox("Category:", list(var_groups.keys()))
    target_var = st.selectbox("Variable:", var_groups[target_cat])

    # 3. Run Test
    d1 = df[df[group_var] == g1][target_var].dropna()
    d2 = df[df[group_var] == g2][target_var].dropna()

    if len(d1) > 1 and len(d2) > 1:
        t_stat, p_val = ttest_ind(d1, d2)

        st.markdown("### Results")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"{g1} Mean", f"{d1.mean():.2f}", f"n={len(d1)}")
        col2.metric(f"{g2} Mean", f"{d2.mean():.2f}", f"n={len(d2)}")
        col3.metric("Difference", f"{d2.mean() - d1.mean():.2f}")
        col4.metric("P-Value", f"{p_val:.4e}", delta_color="inverse" if p_val < 0.05 else "off")

        # Plot
        fig, ax = plt.subplots(figsize=(8, 5))
        plot_data = df[df[group_var].isin([g1, g2])]
        sns.boxplot(x=group_var, y=target_var, data=plot_data, palette="Set2", width=0.5, ax=ax, showfliers=False)
        sns.stripplot(x=group_var, y=target_var, data=plot_data, color='black', alpha=0.5, jitter=True, ax=ax)
        ax.set_title(f"{target_var} by {group_var}")
        st.pyplot(fig)

# --- MODULE 4: REGRESSION ---
elif module == "📐 Regression Analysis":
    st.header("Multivariable Regression")

    st.markdown("##### 1. Outcome Variable (Y)")
    y_cat = st.selectbox("Y Category:", list(var_groups.keys()), key='y_cat')
    y_var = st.selectbox("Y Variable:", var_groups[y_cat], key='y_var')

    st.markdown("##### 2. Predictors (X)")
    x_vars = st.multiselect("Select Independent Variables (X):", num_cols, default=['Age_years', 'BMI'])

    if st.button("Run Regression"):
        if x_vars:
            reg_df = df[[y_var] + x_vars].dropna()
            model = sm.OLS(reg_df[y_var], sm.add_constant(reg_df[x_vars])).fit()
            st.text(model.summary())

            # Diagnostic Plot
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.scatter(model.fittedvalues, model.resid, alpha=0.5)
            ax.axhline(0, color='red', linestyle='--')
            ax.set_xlabel("Fitted Values")
            ax.set_ylabel("Residuals")
            ax.set_title("Residuals vs Fitted")
            st.pyplot(fig)

# --- MODULE 5: CORRELATION ---
elif module == "🔥 Correlation Matrix":
    st.header("Correlation Matrix")

    cats_to_corr = st.multiselect("Select Categories to Correlate:", list(var_groups.keys()),
                                  default=["📍 Radius (HR-pQCT)", "🩸 Bone Markers"])

    vars_to_corr = []
    for cat in cats_to_corr:
        vars_to_corr.extend(var_groups[cat])

    if len(vars_to_corr) > 1:
        corr_df = df[vars_to_corr].corr()
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_df, cmap='coolwarm', center=0, linewidths=0.5, square=True, ax=ax)
        st.pyplot(fig)
    else:
        st.info("Select categories to generate heatmap.")