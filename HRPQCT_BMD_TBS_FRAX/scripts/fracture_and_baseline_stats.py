import pandas as pd
import numpy as np
from scipy import stats
import os


def classify_fx_site(site):
    """
    Standardizes fracture categorization based on clinical hierarchy.
    MOP (Major Osteoporotic Fracture): Spine, Hip, Wrist/Forearm, Proximal Humerus.
    """
    if pd.isna(site) or str(site).strip().upper() == "NO FRACTURE":
        return None
    site = str(site).upper().strip()

    # MOP/MOF Keywords
    mop_keywords = [
        'HIP', 'SPINE', 'SPINAL', 'L1', 'L2', 'L3', 'D12', 'COLLAPSE', 'BIOCONCAVE',
        'WRIST', 'FOREARM', 'RADIUS', 'LUNATE', 'HUMERUS', 'SHOULDER'
    ]

    is_mop = any(k in site for k in mop_keywords)
    return "MOP" if is_mop else "Other"


def run_comprehensive_analysis():
    # Dynamic path anchoring to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_dir = os.path.join(project_root, "data", "03_final")
    output_dir = os.path.join(project_root, "results", "tables")
    os.makedirs(output_dir, exist_ok=True)

    cohort_files = {
        'total_n215': 'cohort_total_n215.csv',
        'total_dm': 'cohort_total_diabetes.csv',
        'osteopenia_n91': 'cohort_osteopenia_n91.csv',
        'osteo_dm': 'cohort_osteopenia_diabetes.csv'
    }

    summary_stats = []
    baseline_vars = ['AGE', 'BMI', 'L1-L4 T SCORE', 'NECK_TSCORE', 'TBS']

    print(f"🚀 Starting Comprehensive Analysis across {len(cohort_files)} cohorts...")

    for name, filename in cohort_files.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            print(f"⚠️ Warning: {filename} not found. Skipping.")
            continue

        df = pd.read_csv(path)
        df['GROUP'] = df['GROUP'].str.strip()

        # 1. Fracture Distribution (Group A only)
        df_fx = df[df['GROUP'] == 'Group A'].copy()
        df_fx['fx_type'] = df_fx['SITE OF FRACTURE'].apply(classify_fx_site)

        mop_count = (df_fx['fx_type'] == "MOP").sum()
        other_count = (df_fx['fx_type'] == "Other").sum()
        total_fx = len(df_fx)

        # 2. Baseline Comparison (Group A vs Group B)
        df_ctl = df[df['GROUP'] == 'Group B']

        cohort_summary = {
            'Cohort': name,
            'N_Fracture': total_fx,
            'N_Control': len(df_ctl),
            'MOP_N': mop_count,
            'MOP_Percent': (mop_count / total_fx * 100) if total_fx > 0 else 0,
            'Other_N': other_count,
            'Other_Percent': (other_count / total_fx * 100) if total_fx > 0 else 0
        }

        # Calculate means and p-values for continuous variables
        for v in baseline_vars:
            if v in df.columns:
                fx_vals = df_fx[v].dropna()
                ctl_vals = df_ctl[v].dropna()

                m_fx, s_fx = fx_vals.mean(), fx_vals.std()
                m_ct, s_ct = ctl_vals.mean(), ctl_vals.std()
                p = stats.ttest_ind(fx_vals, ctl_vals)[1]

                cohort_summary[f'{v}_Fx'] = f"{m_fx:.2f} ± {s_fx:.2f}"
                cohort_summary[f'{v}_Ctl'] = f"{m_ct:.2f} ± {s_ct:.2f}"
                cohort_summary[f'{v}_P'] = f"{p:.4f}"

        summary_stats.append(cohort_summary)

    # Export unified table
    result_df = pd.DataFrame(summary_stats)
    output_path = os.path.join(output_dir, "unified_baseline_and_fracture_stats.csv")
    result_df.to_csv(output_path, index=False)

    print(f"✅ Analysis complete. Unified results saved to: {output_path}")

    # Specific printout for the Primary Osteopenic Sub-cohort (n=91) as requested
    if 'osteopenia_n91' in result_df['Cohort'].values:
        print("\n--- Summary for Osteopenic Sub-cohort (n=91) ---")
        row = result_df[result_df['Cohort'] == 'osteopenia_n91'].iloc[0]
        print(f"Fracture Distribution: MOP={row['MOP_N']}, Other={row['Other_N']}")
        for v in baseline_vars:
            print(f"{v:15}: {row[f'{v}_Fx']} vs {row[f'{v}_Ctl']} (p={row[f'{v}_P']})")


if __name__ == "__main__":
    run_comprehensive_analysis()