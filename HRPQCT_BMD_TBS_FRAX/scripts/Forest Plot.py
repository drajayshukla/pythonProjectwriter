import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import os


def calculate_quartile_or(df, param, adjusters):
    """Calculates OR per quartile decrease with robustness checks."""
    # Ensure parameter exists (case-insensitive search)
    col = next((c for c in df.columns if c.upper() == param.upper()), None)
    if not col:
        return np.nan, np.nan, np.nan

    temp = df[['GROUP', col] + adjusters].dropna()
    temp['y'] = temp['GROUP'].map({'Group A': 1, 'Group B': 0})

    # Calculate Quartiles: 1 (Lowest) to 4 (Highest)
    # Risk per quartile DECREASE (regress on 5 - Q)
    try:
        temp['Q'] = pd.qcut(temp[col], 4, labels=[1, 2, 3, 4]).astype(float)
        temp['Q_inv'] = 5 - temp['Q']

        X = sm.add_constant(temp[['Q_inv'] + adjusters])
        model = sm.Logit(temp['y'], X).fit(disp=0)

        or_val = np.exp(model.params['Q_inv'])
        conf = np.exp(model.conf_int().loc['Q_inv'])
        return or_val, conf[0], conf[1]
    except:
        return np.nan, np.nan, np.nan


# --- DYNAMIC PATH ANCHORING ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_path = os.path.join(project_root, 'data', '03_final', 'cohort_total_n215.csv')
output_dir = os.path.join(project_root, 'results', 'figures')
os.makedirs(output_dir, exist_ok=True)

# Define Clinical and Structural Parameters
params_mapping = [
    ('Total vBMD', 'RADIUS_ttvBMD', 'TIBIA_ttvBMD'),
    ('Tb.vBMD', 'RADIUS_tbvBMD', 'TIBIA_tbvBMD'),
    ('Ct.Th', 'RADIUS_CT.TH', 'TIBIA_CT.TH'),
    ('Tb.N', 'RADIUS_TB.N', 'TIBIA_TB.N'),
    ('Ct.Po', 'RADIUS_CT.PO', 'TIBIA_CT.PO'),
    ('Stiffness', 'Stiffness_RADIUS', 'Stiffness_TIBIA'),
    ('Failure Load', 'F.Load_RADIUS', 'F.Load_TIBIA')
]

# Load Data
if not os.path.exists(data_path):
    raise FileNotFoundError(f"Missing data file at: {data_path}")

df = pd.read_csv(data_path)
adjusters = ['AGE', 'BMI', 'HT_BMD']  # Standard Clinical Adjusters

# Calculation Loop
radius_results = []
tibia_results = []
valid_labels = []

for label, r_col, t_col in params_mapping:
    r_or, r_l, r_u = calculate_quartile_or(df, r_col, adjusters)
    t_or, t_l, t_u = calculate_quartile_or(df, t_col, adjusters)

    if not np.isnan(r_or) and not np.isnan(t_or):
        radius_results.append((r_or, r_l, r_u))
        tibia_results.append((t_or, t_l, t_u))
        valid_labels.append(label)

# --- PLOTTING ---
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 7))
y_pos = np.arange(len(valid_labels))

# Radius (Black)
ax.errorbar([x[0] for x in radius_results], y_pos + 0.15,
            xerr=[[x[0] - x[1] for x in radius_results], [x[2] - x[0] for x in radius_results]],
            fmt='o', color='black', label='Distal Radius', capsize=5, markersize=8, elinewidth=1.5)

# Tibia (Grey)
ax.errorbar([x[0] for x in tibia_results], y_pos - 0.15,
            xerr=[[x[0] - x[1] for x in tibia_results], [x[2] - x[0] for x in tibia_results]],
            fmt='o', color='darkgrey', label='Distal Tibia', capsize=5, markersize=8, elinewidth=1.5)

ax.axvline(x=1, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(valid_labels, fontsize=11, fontweight='bold')
ax.set_xlabel('Odds Ratio (95% CI) per Quartile Decrease', fontsize=12)
ax.set_title('Fracture Risk per Quartile Decay of Microarchitecture\n(Adjusted for Age, BMI, and Total Hip aBMD)',
             fontsize=14, pad=20)
ax.legend(frameon=True, loc='lower right', fontsize=10)

plt.tight_layout()
save_path = os.path.join(output_dir, 'forest_plot_fracture_risk.png')
plt.savefig(save_path, dpi=300)
print(f"✅ Figure saved successfully: {save_path}")
plt.show()