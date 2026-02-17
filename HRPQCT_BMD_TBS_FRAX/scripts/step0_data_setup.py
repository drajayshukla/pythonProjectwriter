import pandas as pd
import numpy as np
import os


def setup_project_data():
    print("🚀 Starting Data Setup: 'Entry Ticket' + Imputation + Diabetes Subgroups...")

    # --- 1. ABSOLUTE PATH MANAGEMENT ---
    # This ensures files go exactly where you want them
    base_dir = "/Users/dr.ajayshukla/PycharmProjects/pythonProjectwriter/HRPQCT_BMD_TBS_FRAX"
    raw_file = os.path.join(base_dir, "data/01_raw/DBT_final.csv")
    final_dir = os.path.join(base_dir, "data/03_final")

    # Create the output directory if it doesn't exist
    os.makedirs(final_dir, exist_ok=True)
    print(f"📁 Destination Folder: {final_dir}")

    # --- 2. DATA LOADING ---
    if not os.path.exists(raw_file):
        print(f"❌ Error: Raw file not found at {raw_file}")
        return

    print(f"📖 Reading raw data from: {raw_file}")
    df = pd.read_csv(raw_file)
    df.columns = df.columns.str.strip()

    # --- 3. STANDARDIZATION ---
    # Clean Group Names
    df['GROUP'] = df['GROUP'].astype(str).str.strip().str.upper()
    group_map = {'GROUP A': 'Group A', 'GROUP B': 'Group B', 'GROUP C': 'Group C'}
    df['GROUP'] = df['GROUP'].map(group_map).fillna(df['GROUP'])

    # Clean WHO Classification
    if 'WHO CLASSIFICATION' in df.columns:
        df['WHO CLASSIFICATION'] = df['WHO CLASSIFICATION'].astype(str).str.strip().str.upper()

    # Clean Diabetes Status
    if 'TYPE 2 DM' in df.columns:
        df['TYPE 2 DM'] = df['TYPE 2 DM'].astype(str).str.strip().str.upper().replace(['NAN', 'NA'], np.nan)

    # --- 4. THE "ENTRY TICKET" (Inclusion Logic) ---
    # Rule: Valid DXA (L1-L4) AND Valid HR-pQCT (Radius) AND Group A/B (Fracture/Control)
    has_dxa = df['L1-L4 T SCORE'].notna()
    has_hrpqct = df['RADIUS_ttvBMD'].notna()
    is_correct_group = df['GROUP'].isin(['Group A', 'Group B'])

    df_valid = df[has_dxa & has_hrpqct & is_correct_group].copy()

    print(f"   -> Original Rows (Group A+B): {len(df[is_correct_group])}")
    print(f"   -> Valid Scans (Inclusion N=215): {len(df_valid)}")

    # --- 5. IMPUTATION (Missing Value Management) ---
    # A. Numeric Imputation (Mean)
    numeric_cols = df_valid.select_dtypes(include=[np.number]).columns
    df_valid[numeric_cols] = df_valid[numeric_cols].fillna(df_valid[numeric_cols].mean())

    # B. Categorical Imputation (Diabetes Status - Mode)
    # Critical step to recover missing T2DM labels for the N=140 target
    if 'TYPE 2 DM' in df_valid.columns:
        mode_dm = df_valid['TYPE 2 DM'].mode()[0]  # Calculates the most frequent value (likely 'Y')
        missing_count = df_valid['TYPE 2 DM'].isna().sum()
        df_valid['TYPE 2 DM'] = df_valid['TYPE 2 DM'].fillna(mode_dm)
        print(f"   -> ✅ Imputed {missing_count} missing Diabetes status with Mode: '{mode_dm}'")

    # --- 6. SAVE FINAL COHORTS (Hierarchy Aligned) ---

    # 1. Secondary Objective A: Total Cohort (N=215)
    df_valid.to_csv(os.path.join(final_dir, "cohort_total_n215.csv"), index=False)

    # 2. Secondary Objective B: Diabetes Total (Target N=140)
    df_total_dm = df_valid[df_valid['TYPE 2 DM'] == 'Y'].copy()
    df_total_dm.to_csv(os.path.join(final_dir, "cohort_total_diabetes.csv"), index=False)

    # 3. Primary Objective: Osteopenia Cohort (Target N=91)
    # Using strict string matching for safety
    df_osteo = df_valid[df_valid['WHO CLASSIFICATION'].str.contains('OSTEOPENIA', na=False)].copy()
    df_osteo.to_csv(os.path.join(final_dir, "cohort_osteopenia_n91.csv"), index=False)

    # 4. Secondary Objective B: Diabetes Osteopenia (Target N=66)
    df_osteo_dm = df_osteo[df_osteo['TYPE 2 DM'] == 'Y'].copy()
    df_osteo_dm.to_csv(os.path.join(final_dir, "cohort_osteopenia_diabetes.csv"), index=False)

    # --- VERIFICATION PRINT ---
    print("\n📊 --- COHORT VERIFICATION ---")
    print(f"1. Total Cohort (N=215):      {len(df_valid)}")
    print(f"2. Primary Osteopenia (N=91): {len(df_osteo)}")
    print(f"3. Total Diabetes (N=140):    {len(df_total_dm)}")
    print(f"4. Osteopenia Diabetes (N=66):{len(df_osteo_dm)}")
    print(f"\n🎉 SUCCESS! All files saved to: {final_dir}")


if __name__ == "__main__":
    setup_project_data()