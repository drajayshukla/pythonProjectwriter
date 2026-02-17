import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy import stats
import os


def run_frax_adjusted_analysis():
    # Dynamic path anchoring
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

    # Parameters and FRAX adjuster
    bone_params = ['RADIUS_ttvBMD', 'RADIUS_TB.N', 'RADIUS_CT.PO', 'F.Load_RADIUS',
                   'TIBIA_ttvBMD', 'TIBIA_TB.N', 'TIBIA_CT.PO', 'F.Load_TIBIA']
    frax_col = 'FRAX – Major Osteoporotic Fracture (%)'

    print("📊 Executing FRAX-Adjusted Risk Engine...")

    for name, filename in cohort_files.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path): continue

        df = pd.read_csv(path)
        df['target'] = df['GROUP'].map({'Group A': 1, 'Group B': 0})

        # Handle absolute magnitudes for FEA
        for col in ['F.Load_RADIUS', 'F.Load_TIBIA']:
            if col in df.columns: df[col] = df[col].abs()

        results = []
        for param in bone_params:
            if param not in df.columns or frax_col not in df.columns: continue

            # Filter and standardize (Risk per SD decrease)
            temp = df[['target', param, frax_col]].dropna()
            temp['z_param_inv'] = ((temp[param] - temp[param].mean()) / temp[param].std()) * -1

            try:
                X = sm.add_constant(temp[['z_param_inv', frax_col]])
                model = sm.Logit(temp['target'], X).fit(disp=0)
                or_val = np.exp(model.params['z_param_inv'])
                conf = np.exp(model.conf_int().loc['z_param_inv'])

                results.append({
                    'Variable': param,
                    'aOR_FRAX_Adjusted': f"{or_val:.2f} ({conf[0]:.2f}-{conf[1]:.2f})",
                    'P_Value': model.pvalues['z_param_inv']
                })
            except:
                continue

        # Save per cohort
        res_df = pd.DataFrame(results)
        res_df.to_csv(os.path.join(output_dir, f"frax_adjusted_{name}.csv"), index=False)
        print(f"✅ Adjusted stats saved for {name}")


if __name__ == "__main__":
    run_frax_adjusted_analysis()