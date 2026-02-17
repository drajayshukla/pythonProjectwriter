import pandas as pd
import numpy as np
from scipy import stats
import os


def calculate_cohen_d(group1, group2):
    """Calculates Cohen's d using pooled standard deviation."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0: return 0
    return (np.mean(group1) - np.mean(group2)) / pooled_sd


def calculate_auc_from_u(group_fx, group_ctl):
    """Calculates AUC via Mann-Whitney U statistic (Root Cause calculation)."""
    n1, n2 = len(group_fx), len(group_ctl)
    if n1 == 0 or n2 == 0: return np.nan
    u_stat, _ = stats.mannwhitneyu(group_fx, group_ctl, alternative='two-sided')
    auc = u_stat / (n1 * n2)
    return auc if auc >= 0.5 else 1 - auc


def run_stats_pipeline(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"⚠️ Warning: File not found at {input_path}")
        return

    df = pd.read_csv(input_path)
    df.columns = df.columns.str.strip()
    df['GROUP'] = df['GROUP'].astype(str).str.strip()

    grp_a = df[df['GROUP'] == 'Group A']
    grp_b = df[df['GROUP'] == 'Group B']

    variables = [
        'AGE', 'BMI', 'L1-L4 T SCORE', 'NECK_TSCORE', 'TBS',
        'RADIUS_ttvBMD', 'RADIUS_TB.N', 'RADIUS_CT.TH', 'RADIUS_CT.PO',
        'TIBIA_ttvBMD', 'TIBIA_TB.N', 'TIBIA_CT.TH', 'TIBIA_CT.PO',
        'F.Load_RADIUS', 'Stiffness_RADIUS', 'F.Load_TIBIA', 'Stiffness_TIBIA'
    ]

    results = []
    for var in variables:
        if var not in df.columns: continue
        a_vals, b_vals = grp_a[var].dropna(), grp_b[var].dropna()
        if len(a_vals) < 2 or len(b_vals) < 2: continue

        _, p_val = stats.ttest_ind(a_vals, b_vals)
        d = calculate_cohen_d(a_vals, b_vals)
        auc = calculate_auc_from_u(a_vals, b_vals)

        results.append({
            'Variable': var,
            'Mean_Fx': a_vals.mean(), 'SD_Fx': a_vals.std(),
            'Mean_Ctl': b_vals.mean(), 'SD_Ctl': b_vals.std(),
            'P_Value': p_val,
            'Cohen_D': abs(d),
            'AUC': auc
        })

    res_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    res_df.to_csv(output_path, index=False)
    print(f"✅ Successfully processed: {os.path.basename(input_path)}")


if __name__ == "__main__":
    # --- DYNAMIC PATH ANCHORING ---
    # script_path = .../scripts/stats_engine.py
    # project_root = .../HRPQCT_BMD_TBS_FRAX
    script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(script_path))

    data_dir = os.path.join(project_root, "data", "03_final")
    results_dir = os.path.join(project_root, "results", "tables")

    cohort_mappings = {
        "cohort_total_n215.csv": "stats_total.csv",
        "cohort_total_diabetes.csv": "stats_total_dm.csv",
        "cohort_osteopenia_n91.csv": "stats_osteopenia.csv",
        "cohort_osteopenia_diabetes.csv": "stats_osteo_dm.csv"
    }

    print(f"📊 Project Root identified as: {project_root}")
    print("🚀 Executing Clinical Stats Engine...")

    for in_file, out_file in cohort_mappings.items():
        run_stats_pipeline(
            os.path.join(data_dir, in_file),
            os.path.join(results_dir, out_file)
        )

    print("\n🎉 Success! All analysis tables are ready for Quarto integration.")