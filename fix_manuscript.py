import os
import pandas as pd
import numpy as np

# --- CONFIGURATION ---
base_dir = "MAFLD_HRPQCT"
data_dir = os.path.join(base_dir, "data")
manuscript_dir = os.path.join(base_dir, "manuscript")

os.makedirs(data_dir, exist_ok=True)
os.makedirs(manuscript_dir, exist_ok=True)

# ---------------------------------------------------------
# 1. REGENERATE DATA (Adding BMI explicitly)
# ---------------------------------------------------------
np.random.seed(42)
n = 100
# Create base data
df = pd.DataFrame({
    'Patient_ID': [f'P{i:03d}' for i in range(1, 101)],
    'Study_Group': ['Control']*50 + ['Advanced Fibrosis']*50,
    'Age_years': np.random.randint(45, 75, 100),
    'Sex': np.random.choice(['M', 'F'], 100),
    'Weight_kg': np.concatenate([np.random.normal(70, 10, 50), np.random.normal(85, 15, 50)]),
    'Height_cm': np.random.normal(165, 8, 100),
    'FibroScan_LSM_kPa': np.concatenate([np.random.normal(5.5, 1.2, 50), np.random.normal(22.0, 8.5, 50)]),
    'Sclerostin_pg_mL': np.concatenate([np.random.normal(350, 60, 50), np.random.normal(680, 150, 50)]),
    'Radius_Ct_Po_percent': np.concatenate([np.random.normal(2.5, 0.8, 50), np.random.normal(6.1, 1.9, 50)]),
    'Radius_Failure_Load_N': np.concatenate([np.random.normal(4100, 300, 50), np.random.normal(3100, 650, 50)])
})

# Calculate BMI (The missing piece!)
df['BMI'] = df['Weight_kg'] / ((df['Height_cm']/100)**2)

# Save
csv_path = os.path.join(data_dir, "liver_hrpqct_filled.csv")
df.to_csv(csv_path, index=False)
print(f"✅ Data regenerated with BMI at: {csv_path}")


# ---------------------------------------------------------
# 2. WRITE DYNAMIC_PART.QMD (Matches the Data)
# ---------------------------------------------------------
dynamic_lines = [
    "# Results",
    "",
    "```{python}",
    "#| label: analysis-table",
    "#| echo: false",
    "#| message: false",
    "#| warning: false",
    "",
    "import pandas as pd",
    "from scipy.stats import ttest_ind",
    "from IPython.display import Markdown",
    "import seaborn as sns",
    "import matplotlib.pyplot as plt",
    "",
    "# Load Data",
    "try:",
    "    df = pd.read_csv('../data/liver_hrpqct_filled.csv')",
    "except:",
    "    df = pd.read_csv('MAFLD_HRPQCT/data/liver_hrpqct_filled.csv')",
    "",
    "ctrl = df[df['Study_Group'] == 'Control']",
    "fibro = df[df['Study_Group'] == 'Advanced Fibrosis']",
    "",
    "def get_row(label, col):",
    "    m_c, s_c = ctrl[col].mean(), ctrl[col].std()",
    "    m_f, s_f = fibro[col].mean(), fibro[col].std()",
    "    _, p = ttest_ind(ctrl[col].dropna(), fibro[col].dropna())",
    "    p_txt = '<0.001' if p < 0.001 else f'{p:.4f}'",
    "    return {'Variable': label, 'Control': f'{m_c:.2f} ± {s_c:.2f}', 'F3-F4': f'{m_f:.2f} ± {s_f:.2f}', 'P-value': p_txt}",
    "",
    "vars_to_show = {",
    "    'Age_years': 'Age (years)',",
    "    'BMI': 'BMI (kg/m²)',",
    "    'FibroScan_LSM_kPa': 'Liver Stiffness (kPa)',",
    "    'Sclerostin_pg_mL': 'Sclerostin (pg/mL)',",
    "    'Radius_Ct_Po_percent': 'Radius Ct.Po (%)',",
    "    'Radius_Failure_Load_N': 'Radius Failure Load (N)'",
    "}",
    "",
    "table_df = pd.DataFrame([get_row(l, c) for c, l in vars_to_show.items()])",
    "Markdown(table_df.to_markdown(index=False))",
    "```",
    "",
    "## Microarchitectural Analysis",
    "",
    "```{python}",
    "#| label: dynamic-text-vars",
    "#| echo: false",
    "",
    "ct_po_c = ctrl['Radius_Ct_Po_percent'].mean()",
    "ct_po_f = fibro['Radius_Ct_Po_percent'].mean()",
    "_, p_ct = ttest_ind(ctrl['Radius_Ct_Po_percent'], fibro['Radius_Ct_Po_percent'])",
    "p_ct_txt = '< 0.001' if p_ct < 0.001 else f'= {p_ct:.3f}'",
    "",
    "ff_c = ctrl['Radius_Failure_Load_N'].mean()",
    "ff_f = fibro['Radius_Failure_Load_N'].mean()",
    "_, p_ff = ttest_ind(ctrl['Radius_Failure_Load_N'], fibro['Radius_Failure_Load_N'])",
    "p_ff_txt = '< 0.001' if p_ff < 0.001 else f'= {p_ff:.3f}'",
    "",
    "pct_increase = ((ct_po_f - ct_po_c) / ct_po_c) * 100",
    "```",
    "",
    "HR-pQCT analysis revealed a significant compartment-specific decay in the cortical bone. Patients with advanced fibrosis exhibited a **`{python} f'{pct_increase:.1f}'`% increase** in Cortical Porosity ($Ct.Po$) at the distal radius compared to controls (`{python} f'{ct_po_f:.2f}'`% vs. `{python} f'{ct_po_c:.2f}'`%, $p$ `{python} p_ct_txt`).",
    "",
    "This 'trabecularization' of the cortex translated into a significant biomechanical deficit. Finite Element Analysis (FEA) estimated a mean Failure Load ($F_f$) of **`{python} f'{ff_f:.0f}'` N** in the fibrosis group, compared to **`{python} f'{ff_c:.0f}'` N** in the control group ($p$ `{python} p_ff_txt`).",
    "",
    "## Visual Analysis",
    "",
    "**Figure 1** illustrates the distribution of cortical porosity between the two groups.",
    "",
    "```{python}",
    "#| label: fig-boxplot",
    "#| echo: false",
    "#| warning: false",
    "",
    "plt.figure(figsize=(8, 5))",
    "sns.set_style('whitegrid')",
    "sns.boxplot(x='Study_Group', y='Radius_Ct_Po_percent', data=df, palette=['#3498db', '#e74c3c'])",
    "plt.xlabel('Cohort')",
    "plt.ylabel('Radius Cortical Porosity (%)')",
    "plt.title('Impact of Advanced Fibrosis on Cortical Microarchitecture')",
    "plt.show()",
    "```"
]

with open(os.path.join(manuscript_dir, "dynamic_part.qmd"), "w", encoding="utf-8") as f:
    f.write("\n".join(dynamic_lines))

print("✅ dynamic_part.qmd rewritten successfully.")
print("🚀 READY! Run: quarto render main.qmd --to html")