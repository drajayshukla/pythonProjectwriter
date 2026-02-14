import os
import pandas as pd
import numpy as np

# 1. Setup Folders
base_dir = "MAFLD_HRPQCT"
data_dir = os.path.join(base_dir, "data")
manuscript_dir = os.path.join(base_dir, "manuscript")

os.makedirs(data_dir, exist_ok=True)
os.makedirs(manuscript_dir, exist_ok=True)

# 2. Generate Dummy Data
np.random.seed(42)
df = pd.DataFrame({
    'Patient_ID': [f'P{i:03d}' for i in range(1, 101)],
    'Study_Group': ['Control']*50 + ['Advanced Fibrosis']*50,
    'Age_years': np.random.randint(45, 75, 100),
    'Sex': np.random.choice(['M', 'F'], 100),
    'FibroScan_LSM_kPa': np.concatenate([np.random.normal(5, 1, 50), np.random.normal(21, 9, 50)]),
    'Albumin_g_dL': np.concatenate([np.random.normal(4.2, 0.3, 50), np.random.normal(3.5, 0.5, 50)]),
    'Sclerostin_pg_mL': np.concatenate([np.random.normal(380, 70, 50), np.random.normal(670, 170, 50)]),
    'IGF1_ng_mL': np.concatenate([np.random.normal(160, 30, 50), np.random.normal(90, 20, 50)]),
    'Radius_Ct_Po_percent': np.concatenate([np.random.normal(2.8, 0.9, 50), np.random.normal(5.5, 1.8, 50)]),
    'Radius_Failure_Load_N': np.concatenate([np.random.normal(3800, 350, 50), np.random.normal(3200, 600, 50)]),
    'BMI': np.concatenate([np.random.normal(24, 4, 50), np.random.normal(28, 6, 50)])
})
df.to_csv(os.path.join(data_dir, "liver_hrpqct_filled.csv"), index=False)

# 3. Write the QMD file using a cleaner string method
qmd_body = [
    '---',
    'title: "Results: Baseline Characteristics and Microarchitectural Analysis"',
    'format:',
    '  html:',
    '    code-fold: true',
    '    theme: cosmo',
    '  pdf:',
    '    echo: false',
    '---',
    '',
    '# Baseline Characteristics',
    '',
    'The study population consisted of 100 participants. Results are summarized in **Table 1**.',
    '',
    '```{python}',
    '#| label: setup',
    '#| echo: false',
    'import pandas as pd',
    'from scipy.stats import ttest_ind',
    'import seaborn as sns',
    'import matplotlib.pyplot as plt',
    'from IPython.display import Markdown',
    '',
    'df = pd.read_csv("../data/liver_hrpqct_filled.csv")',
    'ctrl = df[df["Study_Group"] == "Control"]',
    'fibro = df[df["Study_Group"] == "Advanced Fibrosis"]',
    '',
    'def get_row(label, col):',
    '    m_c, s_c = ctrl[col].mean(), ctrl[col].std()',
    '    m_f, s_f = fibro[col].mean(), fibro[col].std()',
    '    _, p = ttest_ind(ctrl[col].dropna(), fibro[col].dropna())',
    '    p_txt = "<0.001" if p < 0.001 else f"{p:.4f}"',
    '    return {"Variable": label, "Control": f"{m_c:.2f}±{s_c:.2f}", "F3-F4": f"{m_f:.2f}±{s_f:.2f}", "P-value": p_txt}',
    '',
    'vars = {"Age_years": "Age", "BMI": "BMI", "FibroScan_LSM_kPa": "LSM", "Sclerostin_pg_mL": "Sclerostin", "Radius_Ct_Po_percent": "Ct.Po (%)", "Radius_Failure_Load_N": "Failure Load (N)"}',
    'table_df = pd.DataFrame([get_row(l, c) for c, l in vars.items()])',
    'Markdown(table_df.to_markdown(index=False))',
    '```',
    '',
    '# Visual Analysis',
    '',
    '```{python}',
    '#| echo: false',
    'sns.boxplot(x="Study_Group", y="Radius_Ct_Po_percent", data=df)',
    'plt.title("Cortical Porosity Comparison")',
    'plt.show()',
    '```'
]

with open(os.path.join(manuscript_dir, "results_dynamic.qmd"), "w") as f:
    f.write("\n".join(qmd_body))

print("✅ Setup successful. Run 'quarto render' now.")