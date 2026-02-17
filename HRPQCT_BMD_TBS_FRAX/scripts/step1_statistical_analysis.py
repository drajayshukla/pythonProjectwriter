import pandas as pd
import numpy as np
from scipy import stats
import os


# --- CORE STATISTICAL FUNCTIONS ---

def calculate_cohen_d(group_fx, group_ctl):
    """Calculates Cohen's d for Effect Size using pooled standard deviation."""
    n1, n2 = len(group_fx), len(group_ctl)
    var1, var2 = np.var(group_fx, ddof=1), np.var(group_ctl, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0: return 0
    return (np.mean(group_fx) - np.mean(group_ctl)) / pooled_sd


def calculate_auc_from_u(group_fx, group_ctl):
    """
    Calculates AUC using the Mann-Whitney U statistic (First Principles).
    AUC = U / (n1 * n2)
    """
    n1, n2 = len(group_fx), len(group_ctl)
    if n1 == 0 or n2 == 0: return np.nan

    # Calculate Mann-Whitney U
    # We use the 'two-sided' U-statistic to find the area
    u_stat, _ = stats.mannwhitneyu(group_fx, group_ctl, alternative='two-sided')

    # Calculate AUC
    auc = u_stat / (n1 * n2)

    # Standardize AUC to represent discrimination capacity (>= 0.5)
    return auc if auc >= 0.5 else 1 - auc


def run_stats_analysis(df, variables, output_path):
    """Performs t-test, Cohen's d, and AUC for a list of variables."""
    results = []

    # Identify Groups (Standardize names for robustness)
    df['GROUP'] = df['GROUP'].astype(str).str.strip()
    grp_fx = df[df['GROUP'] == 'Group A']
    grp_ctl = df[df['GROUP'] == 'Group B']

    for var in variables:
        if var not in df.columns:
            continue

        # Extract data and drop NaNs for this specific variable
        x_fx = grp_fx[var].dropna()
        x_ctl = grp_ctl[var].dropna()

        if len(x_fx) < 2 or len(x_ctl) < 2:
            continue

        # 1. Independent T-Test (Standard of JBMR)
        _, p_val = stats.ttest_ind(x_fx, x_ctl)

        # 2. Cohen's D (Effect Size)
        d = calculate_cohen_d(x_fx, x_ctl)

        # 3. AUC via First Principles (Mann-Whitney U)
        auc = calculate_auc_from_u(x_fx, x_ctl)

        results.append({
            'Variable': var,
            'Mean_Fx': np.mean(x_fx),
            'SD_Fx': np.std(x_fx),
            'Mean_Ctl': np.mean(x_ctl),
            'SD_Ctl': np.std(x_ctl),
            'P_Value': p_val,
            'Cohen_D': abs(d),
            'AUC': auc
        })

    res_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    res_df.to_csv(output_path, index=False)
    return res_df


# --- EXECUTION PIPELINE ---

def main():
    # Dynamic Path Management
    # Anchors the paths relative to the location of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data", "03_final")
    table_dir = os.path.join(project_root, "results", "tables")

    os.makedirs(table_dir, exist_ok=True)

    # Variables for analysis
    target_vars = [
        'AGE', 'BMI',
        'L1-L4 T SCORE', 'NECK_TSCORE', 'HT_TSCORE', 'TBS',
        'FRAX – Major Osteoporotic Fracture (%)', 'FRAX – Hip Fracture (%)',
        'RADIUS_ttvBMD', 'RADIUS_TB.N', 'RADIUS_CT.PO', 'RADIUS_CT.TH',
        'TIBIA_ttvBMD', 'TIBIA_TB.N', 'TIBIA_CT.PO', 'TIBIA_CT.TH',
        'F.Load_RADIUS', 'Stiffness_RADIUS', 'F.Load_TIBIA', 'Stiffness_TIBIA'
    ]

    cohort_files = {
        'total_n215': 'cohort_total_n215.csv',
        'total_diabetes': 'cohort_total_diabetes.csv',
        'osteopenia_n91': 'cohort_osteopenia_n91.csv',
        'osteopenia_diabetes': 'cohort_osteopenia_diabetes.csv'
    }

    print(f"📊 Project Root: {project_root}")
    print("🚀 Executing Clinical Stats Engine...")

    for name, filename in cohort_files.items():
        input_file = os.path.join(data_dir, filename)
        output_file = os.path.join(table_dir, f"stats_{name}.csv")

        if os.path.exists(input_file):
            df = pd.read_csv(input_file)
            run_stats_analysis(df, target_vars, output_file)
            print(f"✅ Calculated statistics for {name} -> results/tables/stats_{name}.csv")
        else:
            print(f"⚠️ Warning: File not found at {input_file}")

    print("\n🎉 Analysis Complete. Ready for Quarto integration.")


if __name__ == "__main__":
    main()