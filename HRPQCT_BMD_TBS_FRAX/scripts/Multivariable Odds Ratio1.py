import pandas as pd
import numpy as np
import statsmodels.api as sm
import os


def generate_table_3_values(file_path, cohort_label):
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)
    df['target'] = df['GROUP'].map({'Group A': 1, 'Group B': 0})

    # Bone Parameters for Table 3
    params = ['RADIUS_ttvBMD', 'RADIUS_TB.N', 'RADIUS_CT.PO', 'F.Load_RADIUS',
              'TIBIA_ttvBMD', 'TIBIA_TB.N', 'TIBIA_CT.PO', 'F.Load_TIBIA']

    results = []
    for p in params:
        if p not in df.columns: continue

        # Model 3: Adjusted for Age, BMI, and Total Hip BMD (HT_BMD)
        cols = [p, 'AGE', 'BMI', 'HT_BMD', 'target']
        temp = df[cols].dropna()

        # Standardize for OR per 1-SD decrease
        # Note: For Ct.Po, we calculate per 1-SD increase
        multiplier = 1 if 'PO' in p else -1
        temp['z_val'] = ((temp[p] - temp[p].mean()) / temp[p].std()) * multiplier

        try:
            X = sm.add_constant(temp[['z_val', 'AGE', 'BMI', 'HT_BMD']])
            model = sm.Logit(temp['target'], X).fit(disp=0)
            or_val = np.exp(model.params['z_val'])
            ci = np.exp(model.conf_int().loc['z_val'])
            p_val = model.pvalues['z_val']

            results.append({
                'Parameter': p,
                'aOR': f"{or_val:.2f} ({ci[0]:.2f}-{ci[1]:.2f})",
                'P': p_val
            })
        except:
            continue

    return pd.DataFrame(results)


# Pipeline execution
cohorts = {
    'total': 'data/03_final/cohort_total_n215.csv',
    'total_dm': 'data/03_final/cohort_total_diabetes.csv',
    'osteopenia': 'data/03_final/cohort_osteopenia_n91.csv',
    'osteo_dm': 'data/03_final/cohort_osteopenia_diabetes.csv'
}

for name, path in cohorts.items():
    res = generate_table_3_values(path, name)
    if res is not None:
        res.to_csv(f'results/tables/Table3_OR_{name}.csv', index=False)