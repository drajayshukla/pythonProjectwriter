import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import os


def run_advanced_stats(file_path, cohort_name):
    if not os.path.exists(file_path):
        return

    df = pd.read_csv(file_path)
    df['target'] = df['GROUP'].map({'Group A': 1, 'Group B': 0})

    # 1. CATEGORICAL ANALYSIS (Baseline Characteristics)
    cat_vars = ['CURRENT SMOKING', 'GLUCOTICOID THERAPY', 'TYPE 2 DM', 'RA', 'SECONDARY OSTEOPOROSIS']
    cat_results = []

    for var in cat_vars:
        if var not in df.columns: continue
        contingency = pd.crosstab(df[var], df['GROUP'])

        # Choice: Fisher's Exact if any cell < 5, else Chi-Square
        if (contingency < 5).any().any():
            _, p = stats.fisher_exact(contingency)
            test_type = "Fisher's"
        else:
            _, p, _, _ = stats.chi2_contingency(contingency)
            test_type = "Chi-Square"

        cat_results.append({'Variable': var, 'P_Value': p, 'Test': test_type})

    # 2. CONTINUOUS ANALYSIS (Normality-Aware)
    cont_vars = ['AGE', 'BMI', 'L1-L4 T SCORE', 'NECK_TSCORE', 'TBS',
                 'RADIUS_TB.N', 'RADIUS_CT.PO', 'F.Load_RADIUS',
                 'TIBIA_TB.N', 'TIBIA_CT.PO', 'F.Load_TIBIA']
    cont_results = []

    for var in cont_vars:
        if var not in df.columns: continue
        gA = df[df['target'] == 1][var].dropna()
        gB = df[df['target'] == 0][var].dropna()

        # Shapiro-Wilk for Normality
        _, p_norm = stats.shapiro(df[var].dropna())

        if p_norm > 0.05:
            _, p_val = stats.ttest_ind(gA, gB)
            test_type = "T-test"
        else:
            _, p_val = stats.mannwhitneyu(gA, gB)
            test_type = "Mann-Whitney"

        cont_results.append({'Variable': var, 'P_Value': p_val, 'Test': test_type,
                             'Mean_Fx': gA.mean(), 'SD_Fx': gA.std(),
                             'Mean_Ctl': gB.mean(), 'SD_Ctl': gB.std()})

    # 3. LOGISTIC REGRESSION (Adjusted Odds Ratios)
    # JBMR Standard: Odds Ratio per 1-SD decrease
    log_results = []
    for var in cont_vars:
        if var in ['AGE', 'BMI'] or var not in df.columns: continue

        # Prepare Data: Adjust for Age and BMI
        sub_df = df[[var, 'AGE', 'BMI', 'target']].dropna()

        # Standardize independent variable to get OR per SD
        # We invert the scale (multiply by -1) so OR represents risk per SD DECREASE
        sub_df['z_var'] = ((sub_df[var] - sub_df[var].mean()) / sub_df[var].std()) * -1

        X = sm.add_constant(sub_df[['z_var', 'AGE', 'BMI']])
        model = sm.Logit(sub_df['target'], X).fit(disp=0)

        or_val = np.exp(model.params['z_var'])
        conf = np.exp(model.conf_int().loc['z_var'])
        p_val = model.pvalues['z_var']

        log_results.append({
            'Variable': var,
            'aOR (per SD decrease)': f"{or_val:.2f} ({conf[0]:.2f}-{conf[1]:.2f})",
            'P_Value': p_val
        })

    # Exporting
    os.makedirs('results/tables/advanced', exist_ok=True)
    pd.DataFrame(cat_results).to_csv(f'results/tables/advanced/categorical_{cohort_name}.csv', index=False)
    pd.DataFrame(cont_results).to_csv(f'results/tables/advanced/continuous_{cohort_name}.csv', index=False)
    pd.DataFrame(log_results).to_csv(f'results/tables/advanced/logistic_OR_{cohort_name}.csv', index=False)
    print(f"✅ Advanced stats complete for {cohort_name}")


if __name__ == "__main__":
    cohorts = {
        'data/03_final/cohort_total_n215.csv': 'total',
        'data/03_final/cohort_osteopenia_n91.csv': 'osteopenia'
    }
    for path, name in cohorts.items():
        run_advanced_stats(path, name)