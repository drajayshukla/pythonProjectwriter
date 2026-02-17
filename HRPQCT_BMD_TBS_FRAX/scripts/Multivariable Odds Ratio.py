import pandas as pd
import numpy as np
import statsmodels.api as sm
import os


def calculate_adjusted_ors(file_path, cohort_name):
    if not os.path.exists(file_path):
        return None

    df = pd.read_csv(file_path)
    df['target'] = df['GROUP'].map({'Group A': 1, 'Group B': 0})

    # Core Parameters
    params = ['RADIUS_ttvBMD', 'RADIUS_TB.N', 'RADIUS_CT.PO', 'F.Load_RADIUS',
              'TIBIA_ttvBMD', 'TIBIA_TB.N', 'TIBIA_CT.PO', 'F.Load_TIBIA']

    results = []
    for p in params:
        if p not in df.columns: continue

        # We model Model 3: Adj for Age, BMI, and Total Hip BMD
        cols = [p, 'AGE', 'BMI', 'HT_BMD', 'target']
        temp = df[cols].dropna()

        # Standardize parameter to get OR per 1-SD DECREASE
        temp['z_p'] = ((temp[p] - temp[p].mean()) / temp[p].std()) * -1

        try:
            X = sm.add_constant(temp[['z_p', 'AGE', 'BMI', 'HT_BMD']])
            model = sm.Logit(temp['target'], X).fit(disp=0)
            or_val = np.exp(model.params['z_p'])
            ci = np.exp(model.conf_int().loc['z_p'])
            p_val = model.pvalues['z_p']

            results.append({
                'Parameter': p,
                'aOR': f"{or_val:.2f} ({ci[0]:.2f}-{ci[1]:.2f})",
                'P': p_val
            })
        except:
            continue

    res_df = pd.DataFrame(results)
    res_df.to_csv(f'results/tables/multivariable_OR_{cohort_name}.csv', index=False)
    return res_df


# Execute for all cohorts
cohort_paths = {
    'total': 'data/03_final/cohort_total_n215.csv',
    'total_dm': 'data/03_final/cohort_total_diabetes.csv',
    'osteopenia': 'data/03_final/cohort_osteopenia_n91.csv',
    'osteo_dm': 'data/03_final/cohort_osteopenia_diabetes.csv'
}

for name, path in cohort_paths.items():
    calculate_adjusted_ors(path, name)