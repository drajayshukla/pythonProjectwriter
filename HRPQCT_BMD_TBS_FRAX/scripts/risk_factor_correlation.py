import pandas as pd
import numpy as np
import os
from scipy import stats


def analyze_risk_factors():
    # Path anchoring
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, 'data', '03_final', 'cohort_total_n215.csv')

    if not os.path.exists(data_path):
        return

    df = pd.read_csv(data_path)

    # Define Clinical Risk Factors (Categorical)
    risk_factors = ['TYPE 2 DM', 'GLUCOTICOID THERAPY', 'RA', 'CURRENT SMOKING']
    # Define Bone Biology Outcomes
    bone_outcomes = ['RADIUS_TB.N', 'RADIUS_CT.PO', 'F.Load_RADIUS', 'TIBIA_TB.N', 'TIBIA_CT.PO', 'F.Load_TIBIA']

    print("🔬 Analysis of Clinical Risk Factors on Bone Microarchitecture (Total Cohort N=215)\n")

    results = []
    for factor in risk_factors:
        if factor not in df.columns: continue

        # Split into Presence (Y) vs Absence (N)
        grp_y = df[df[factor] == 'Y']
        grp_n = df[df[factor] == 'N']

        if len(grp_y) < 5: continue

        for outcome in bone_outcomes:
            if outcome not in df.columns: continue

            y_vals = grp_y[outcome].dropna()
            n_vals = grp_n[outcome].dropna()

            # T-test for difference
            t_stat, p_val = stats.ttest_ind(y_vals, n_vals)

            # Effect Size (Cohen's d)
            diff = y_vals.mean() - n_vals.mean()
            pooled_sd = np.sqrt((y_vals.std() ** 2 + n_vals.std() ** 2) / 2)
            d = diff / pooled_sd

            if p_val < 0.05:
                print(f"✅ {factor:20} significantly impacts {outcome:15} (p={p_val:.3f}, d={d:.2f})")


if __name__ == "__main__":
    analyze_risk_factors()