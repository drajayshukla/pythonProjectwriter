import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.linear_model import LogisticRegression
import os


def run_stats_engine():
    print("🚀 Starting Statistics Engine (Golden Thread Aligned)...")

    # --- 1. PATH SETUP ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Input Data Path
    data_path = os.path.join(project_root, "data", "03_final")

    # Output Paths
    tables_path = os.path.join(project_root, "results", "tables")
    figures_path = os.path.join(project_root, "results", "figures")

    # Ensure output directories exist
    os.makedirs(tables_path, exist_ok=True)
    os.makedirs(figures_path, exist_ok=True)

    # --- 2. DATA LOADING ---
    print("...Loading Final Cohort Data")
    try:
        df_osteo = pd.read_csv(os.path.join(data_path, "cohort_osteopenia_n91.csv"))
        df_total = pd.read_csv(os.path.join(data_path, "cohort_total_n215.csv"))
        df_dm_osteo = pd.read_csv(os.path.join(data_path, "cohort_osteopenia_diabetes.csv"))

        # Ensure column names are stripped of whitespace
        df_osteo.columns = df_osteo.columns.str.strip()
        df_total.columns = df_total.columns.str.strip()
        df_dm_osteo.columns = df_dm_osteo.columns.str.strip()

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    # --- 3. STATISTICAL HELPERS ---
    def get_cohens_d(group1, group2):
        """Calculates Cohen's d using pooled standard deviation."""
        n1, n2 = len(group1), len(group2)
        if n1 < 2 or n2 < 2: return 0.0

        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

        if pooled_sd == 0: return 0.0
        return (np.mean(group1) - np.mean(group2)) / pooled_sd

    def calculate_auc_mannwhitney(group_fx, group_ctl):
        """Calculates AUC via Mann-Whitney U."""
        n1, n2 = len(group_fx), len(group_ctl)
        if n1 == 0 or n2 == 0: return 0.5
        u_stat, _ = stats.mannwhitneyu(group_fx, group_ctl, alternative='two-sided')
        auc_val = u_stat / (n1 * n2)
        return auc_val if auc_val >= 0.5 else 1 - auc_val

    def generate_markdown_table(df, vars_dict, title, filename):
        """Generates a Markdown table with Mean, SD, P-value, and Effect Size."""
        filepath = os.path.join(tables_path, filename)

        # Robust Grouping: Filter for Fracture (A) vs Control (B)
        fx = df[
            df['GROUP'].astype(str).str.upper().str.contains('A') | df['GROUP'].astype(str).str.upper().str.contains(
                'FRACTURE')]
        ctl = df[
            df['GROUP'].astype(str).str.upper().str.contains('B') | df['GROUP'].astype(str).str.upper().str.contains(
                'CONTROL')]

        if len(fx) == 0 or len(ctl) == 0:
            print(f"⚠️ Warning: Groups empty for {filename}. Skipping.")
            return

        with open(filepath, 'w') as f:
            f.write(f"**{title}**\n\n")
            f.write(
                f"| Parameter | Fracture (n={len(fx)}) | Control (n={len(ctl)}) | % Diff | P-value | Cohen's d | AUC |\n")
            f.write("|:---|:---:|:---:|:---:|:---:|:---:|:---:|\n")

            for col_key, label in vars_dict.items():
                # Find column (handle case sensitivity/substrings)
                col_match = [c for c in df.columns if col_key in c]
                if not col_match: continue
                actual_col = col_match[0]

                d_fx = pd.to_numeric(fx[actual_col], errors='coerce').dropna()
                d_ctl = pd.to_numeric(ctl[actual_col], errors='coerce').dropna()

                if len(d_fx) < 2 or len(d_ctl) < 2: continue

                # Statistics
                m_fx, s_fx = np.mean(d_fx), np.std(d_fx, ddof=1)
                m_ctl, s_ctl = np.mean(d_ctl), np.std(d_ctl, ddof=1)

                # T-test
                _, p = stats.ttest_ind(d_fx, d_ctl, equal_var=False)

                # Effect Sizes
                d = get_cohens_d(d_fx, d_ctl)
                auc_val = calculate_auc_mannwhitney(d_fx, d_ctl)

                # Percent Difference
                diff = ((m_fx - m_ctl) / m_ctl * 100) if m_ctl != 0 else 0

                # Formatting
                p_fmt = "**<0.001**" if p < 0.001 else (f"**{p:.3f}**" if p < 0.05 else f"{p:.3f}")

                row = f"| {label} | {m_fx:.2f} ± {s_fx:.2f} | {m_ctl:.2f} ± {s_ctl:.2f} | {diff:.1f}% | {p_fmt} | {abs(d):.2f} | {auc_val:.2f} |\n"
                f.write(row)

        print(f"✅ Generated Table: {filename}")

    # --- 4. EXECUTE ANALYSIS (HIERARCHY ALIGNED) ---

    # ---------------------------------------------------------
    # PRIMARY OBJECTIVE: OSTEOPENIA SUBGROUP (n=91)
    # Focus: Trabecular Disconnection & Biomechanical Failure
    # ---------------------------------------------------------
    print("\n--- Processing Primary Objective (n=91) ---")

    # Table 1: Clinical Characteristics (Demographics + DXA)
    clin_vars = {
        'AGE': 'Age (years)',
        'BMI': 'BMI (kg/m²)',
        'L1-L4 T SCORE': 'L1-L4 T-score',
        'NECK_TSCORE': 'Femoral Neck T-score',
        'TBS': 'Trabecular Bone Score (TBS)'
    }
    generate_markdown_table(df_osteo, clin_vars, "Table 1: Clinical Characteristics (Osteopenia Sub-cohort)",
                            "Table1_Clinical.md")

    # Table 2: Structural & Biomechanical (The "Quality" Defect)
    # Note: Adding F.Load if available, otherwise just structural
    struct_vars = {
        'RADIUS_ttvBMD': 'Radius Total vBMD',
        'RADIUS_TB.N': 'Radius Tb.N (1/mm)',
        'RADIUS_TB.SP': 'Radius Tb.Sp (mm)',
        'RADIUS_CT.PO': 'Radius Ct.Po (1)',
        'F.Load': 'Failure Load (N)'  # Matches generic substring
    }
    generate_markdown_table(df_osteo, struct_vars, "Table 2: HR-pQCT & Biomechanics (Osteopenia Sub-cohort)",
                            "Table2_Structural.md")

    # Figure 2: ROC Curve (Diagnostic Superiority)
    print("...Generating Figure 2 (ROC)")
    y_true = df_osteo['GROUP'].astype(str).str.upper().str.contains('A').astype(int)

    # Clean Inputs
    valid_mask = y_true.notna()
    y_clean = y_true[valid_mask]

    # Clinical Model: Age + BMI + Neck T-score
    X_clin = df_osteo[['AGE', 'BMI', 'NECK_TSCORE']].copy()
    X_clin = X_clin.apply(pd.to_numeric, errors='coerce').fillna(X_clin.mean())
    X_clin = X_clin[valid_mask]

    # Structural Model: Age + BMI + Radius Tb.N + Radius vBMD
    # (Using Tb.N as the "Hero" parameter for osteopenia)
    X_struc = df_osteo[['AGE', 'BMI', 'RADIUS_TB.N', 'RADIUS_ttvBMD']].copy()
    X_struc = X_struc.apply(pd.to_numeric, errors='coerce').fillna(X_struc.mean())
    X_struc = X_struc[valid_mask]

    if len(y_clean) > 10 and len(np.unique(y_clean)) > 1:
        clf_clin = LogisticRegression(max_iter=1000).fit(X_clin, y_clean)
        clf_struc = LogisticRegression(max_iter=1000).fit(X_struc, y_clean)

        fp1, tp1, _ = roc_curve(y_clean, clf_clin.predict_proba(X_clin)[:, 1])
        fp2, tp2, _ = roc_curve(y_clean, clf_struc.predict_proba(X_struc)[:, 1])

        auc1, auc2 = auc(fp1, tp1), auc(fp2, tp2)

        plt.figure(figsize=(6, 6))
        plt.plot(fp1, tp1, label=f'Clinical Model (AUC={auc1:.2f})', linestyle='--', color='gray')
        plt.plot(fp2, tp2, label=f'Structural Model (AUC={auc2:.2f})', linewidth=2.5, color='darkblue')
        plt.plot([0, 1], [0, 1], 'k:', alpha=0.3)
        plt.legend(loc='lower right')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Diagnostic Performance in Osteopenia (n=91)')
        plt.grid(True, alpha=0.2)

        plt.savefig(os.path.join(figures_path, "Fig2_ROC.png"), dpi=300)
        plt.close()
        print("✅ Generated Figure: Fig2_ROC.png")
    else:
        print("⚠️ Skipped ROC: Insufficient data points.")

    # ---------------------------------------------------------
    # SECONDARY OBJECTIVE A: GENERAL COHORT (N=215)
    # Focus: Validation & Universal Risk
    # ---------------------------------------------------------
    print("\n--- Processing Secondary Objective A (N=215) ---")

    # Table 3: Validation Table
    # We want to see if Tb.N holds up in the larger group
    val_vars = {
        'RADIUS_TB.N': 'Radius Tb.N (Validation)',
        'RADIUS_CT.PO': 'Radius Ct.Po (Validation)'
    }
    generate_markdown_table(df_total, val_vars, "Table 3: Validation in General Cohort", "Table3_Validation.md")

    # ---------------------------------------------------------
    # SECONDARY OBJECTIVE B: DIABETES PHENOTYPE
    # Focus: The "Cortical Switch"
    # ---------------------------------------------------------
    print("\n--- Processing Secondary Objective B (Diabetes) ---")

    # Table 4: Diabetes Specifics
    # Focus on Ct.Po vs Tb.N to show the "Switch"
    dm_vars = {
        'RADIUS_CT.PO': 'Cortical Porosity (Ct.Po)',
        'RADIUS_TB.N': 'Trabecular Number (Tb.N)'
    }
    generate_markdown_table(df_dm_osteo, dm_vars, "Table 4: Diabetic Osteopenia Phenotype", "Table4_Diabetes.md")

    # Figure 3: Cortical Porosity Boxplot (Visualizing the Switch)
    print("...Generating Figure 3 (Porosity Boxplot)")

    # Prepare Data: Ct.Po for Non-DM Osteopenia vs DM Osteopenia
    # We need to load Non-DM Osteopenia for comparison
    # Non-DM is df_osteo minus df_dm_osteo
    # Simplest way: just look at df_dm_osteo Fracture vs Control first

    dm_fx = df_dm_osteo[df_dm_osteo['GROUP'].astype(str).str.upper().str.contains('A')]['RADIUS_CT.PO'].dropna()
    dm_ctl = df_dm_osteo[df_dm_osteo['GROUP'].astype(str).str.upper().str.contains('B')]['RADIUS_CT.PO'].dropna()

    if len(dm_fx) > 2 and len(dm_ctl) > 2:
        plt.figure(figsize=(5, 6))
        plt.boxplot([dm_ctl, dm_fx], labels=['DM Control', 'DM Fracture'], patch_artist=True,
                    boxprops=dict(facecolor='lightblue'))
        plt.title('Cortical Porosity in Diabetic Osteopenia')
        plt.ylabel('Radius Ct.Po (1)')
        plt.grid(True, axis='y', alpha=0.3)

        plt.savefig(os.path.join(figures_path, "Fig3_Porosity_Diabetes.png"), dpi=300)
        plt.close()
        print("✅ Generated Figure: Fig3_Porosity_Diabetes.png")
    else:
        print("⚠️ Skipped Porosity Plot: Insufficient data.")

    print("\n🎉 Engine Finished. All tables and figures are ready in /results/.")


if __name__ == "__main__":
    run_stats_engine()