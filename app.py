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

# Custom CSS for a cleaner look
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
    st.error(
        "❌ **Critical Error:** Data file not found. Please ensure `liver_hrpqct_filled.csv` is in the `data/` directory.")
    st.stop()

# 3. Sidebar Navigation
st.sidebar.title("Analysis Modules")
module = st.sidebar.radio(
    "Select Module:",
    ["📊 Data Overview", "📈 Descriptive Stats", "🧪 Comparative (T-Test)", "📐 Regression Analysis",
     "🔥 Correlation Matrix"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"**N = {len(df)} Patients**")
st.sidebar.info("Developed for Dr. Ajay Shukla")

# --- MODULE 1: DATA OVERVIEW ---
if module == "📊 Data Overview":
    st.header("Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Patients", len(df))
    col2.metric("Features", len(df.columns))
    col3.metric("Study Groups", len(df['Study_Group'].unique()) if 'Study_Group' in df.columns else "N/A")

    with st.expander("📄 View Raw Data", expanded=True):
        st.dataframe(df.head(10))

    st.subheader("Data Quality Check")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        st.write("Missing Values Detected:", missing[missing > 0])
    else:
        st.success("✅ Dataset is complete (No missing values detected).")

# --- MODULE 2: DESCRIPTIVE STATS ---
elif module == "📈 Descriptive Stats":
    st.header("Descriptive Statistics")

    # Filter for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    default_cols = ['Age_years', 'BMI', 'FibroScan_LSM_kPa', 'Radius_Ct_Po_percent', 'Radius_Failure_Load_N']
    # Ensure defaults exist in data
    default_cols = [c for c in default_cols if c in numeric_cols]

    selected_cols = st.multiselect("Select Variables for Summary Table:", numeric_cols, default=default_cols)

    if selected_cols:
        st.subheader("1. Overall Summary")
        st.dataframe(df[selected_cols].describe().style.format("{:.2f}"))

        if 'Study_Group' in df.columns:
            st.subheader("2. Stratified by Study Group")
            grouped = df.groupby('Study_Group')[selected_cols].describe().T
            st.dataframe(grouped.style.format("{:.2f}"))

# --- MODULE 3: COMPARATIVE ANALYSIS (T-TEST) ---
elif module == "🧪 Comparative (T-Test)":
    st.header("Hypothesis Testing: Group Comparison")

    if 'Study_Group' not in df.columns:
        st.warning("Study_Group column missing.")
        st.stop()

    groups = df['Study_Group'].unique()

    col_setup1, col_setup2 = st.columns(2)
    with col_setup1:
        group1 = st.selectbox("Control Group:", groups, index=0)
    with col_setup2:
        group2 = st.selectbox("Test Group:", groups, index=1 if len(groups) > 1 else 0)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    target_var = st.selectbox("Select Dependent Variable (Y):", numeric_cols, index=numeric_cols.index(
        'Radius_Ct_Po_percent') if 'Radius_Ct_Po_percent' in numeric_cols else 0)

    # Prepare Data
    g1_data = df[df['Study_Group'] == group1][target_var].dropna()
    g2_data = df[df['Study_Group'] == group2][target_var].dropna()

    # Run T-Test
    t_stat, p_val = ttest_ind(g1_data, g2_data)

    # Display Metrics
    st.markdown("### Statistical Results")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"{group1} Mean", f"{g1_data.mean():.2f}", f"σ={g1_data.std():.2f}")
    m2.metric(f"{group2} Mean", f"{g2_data.mean():.2f}", f"σ={g2_data.std():.2f}")
    m3.metric("T-Statistic", f"{t_stat:.2f}")

    # Color code significant P-values
    p_color = "inverse" if p_val < 0.05 else "normal"
    m4.metric("P-Value", f"{p_val:.4e}")

    if p_val < 0.05:
        st.success(f"✅ Statistically Significant Difference (p < 0.05)")
    else:
        st.warning(f"❌ No Significant Difference (p >= 0.05)")

    # Visualization
    st.subheader("Scientific Visualization")
    fig, ax = plt.subplots(figsize=(8, 5))

    # Boxplot with Stripplot overlay (JBMR Style)
    sns.boxplot(x='Study_Group', y=target_var, data=df[df['Study_Group'].isin([group1, group2])],
                palette="Set2", width=0.5, ax=ax, showfliers=False)
    sns.stripplot(x='Study_Group', y=target_var, data=df[df['Study_Group'].isin([group1, group2])],
                  color='black', alpha=0.5, ax=ax, jitter=True)

    ax.set_title(f"Distribution of {target_var} by Group", fontsize=14, fontweight='bold')
    ax.set_xlabel("")
    ax.set_ylabel(target_var, fontsize=12)
    sns.despine()
    st.pyplot(fig)

# --- MODULE 4: REGRESSION ANALYSIS ---
elif module == "📐 Regression Analysis":
    st.header("Multivariable Linear Regression (OLS)")
    st.markdown("Use this module to verify the **'BMI Paradox'** (adjusting for confounders).")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    col1, col2 = st.columns([1, 2])
    with col1:
        y_var = st.selectbox("Dependent Variable (Y):", numeric_cols, index=numeric_cols.index(
            'Radius_Ct_Po_percent') if 'Radius_Ct_Po_percent' in numeric_cols else 0)
    with col2:
        default_x = ['FibroScan_LSM_kPa', 'BMI', 'Age_years']
        default_x = [x for x in default_x if x in numeric_cols]
        x_vars = st.multiselect("Independent Variables (X):", numeric_cols, default=default_x)

    if st.button("🚀 Run Regression Model"):
        if not x_vars:
            st.error("Select at least one independent variable.")
        else:
            # Statsmodels OLS
            reg_df = df[[y_var] + x_vars].dropna()
            Y = reg_df[y_var]
            X = reg_df[x_vars]
            X = sm.add_constant(X)

            model = sm.OLS(Y, X).fit()

            st.subheader("Model Summary")
            st.text(model.summary())

            # Scatter Plot with Regression Line (if 1 predictor)
            if len(x_vars) == 1:
                st.subheader("Regression Plot")
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.regplot(x=x_vars[0], y=y_var, data=reg_df, scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'},
                            ax=ax)
                ax.set_title(f"Correlation: {x_vars[0]} vs {y_var}")
                st.pyplot(fig)

            # Residual Plot (if multiple predictors)
            else:
                st.subheader("Residuals vs Fitted")
                fig, ax = plt.subplots(figsize=(8, 5))
                ax.scatter(model.fittedvalues, model.resid, alpha=0.5)
                ax.axhline(0, color='red', linestyle='--')
                ax.set_xlabel("Fitted Values")
                ax.set_ylabel("Residuals")
                st.pyplot(fig)

# --- MODULE 5: CORRELATION MATRIX ---
elif module == "🔥 Correlation Matrix":
    st.header("Feature Correlation Analysis")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    default_corr = ['FibroScan_LSM_kPa', 'Radius_Ct_Po_percent', 'Radius_Failure_Load_N', 'Sclerostin_pg_mL', 'BMI',
                    'Age_years']
    default_corr = [c for c in default_corr if c in numeric_cols]

    selected_corr_vars = st.multiselect("Select Variables for Heatmap:", numeric_cols, default=default_corr)

    if len(selected_corr_vars) > 1:
        corr_matrix = df[selected_corr_vars].corr()

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt=".2f", linewidths=0.5, ax=ax)
        st.pyplot(fig)
    else:
        st.info("Please select at least two variables to generate the heatmap.")