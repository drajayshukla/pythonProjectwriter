import pandas as pd
import os


def generate_risk_subcohorts():
    print("🚀 Generating Risk Factor Sub-cohorts from Master Database...")

    # --- 1. SETUP PATHS ---
    # Prioritize the specific absolute path provided
    user_path = '/Users/dr.ajayshukla/PycharmProjects/pythonProjectwriter/HRPQCT_BMD_TBS_FRAX/data/01_raw/DBT DATA SAHAJ.xlsx - Sheet1.csv'

    if os.path.exists(user_path):
        raw_path = user_path
    elif os.path.exists('cohort_risk_total.csv'):
        # Fallback: Check current directory
        raw_path = 'cohort_risk_total.csv'
    else:
        # Fallback: Check relative data folder
        raw_path = os.path.join('data', '01_raw', 'cohort_risk_total.csv')

    output_dir = os.path.join('data', '04_risk_factors')
    os.makedirs(output_dir, exist_ok=True)

    print(f"Reading Raw Data from: {raw_path}")
    try:
        df = pd.read_csv(raw_path)
    except FileNotFoundError:
        print(f"❌ Error: Could not find raw file at {raw_path}")
        print("   Please ensure the file exists or update the 'user_path' variable in the script.")
        return

    # --- 2. FILTERING LOGIC ---
    # Define exact column names from your specific file
    col_hrpqct = 'hrpqct done '  # Note the trailing space is critical
    col_bmd = 'BMD DONE OR NOT'
    col_who = 'WHO CLASSIFICATION'
    col_dm = 'DIABETES PRESENT / ABSENT '  # Note the trailing space is critical
    col_t2dm = 'TYPE 2 DM'

    # Logic to handle messy data (e.g. "Hrpqct done" = YES, "Y", "Present")
    def is_positive(val):
        s = str(val).upper().strip()
        if 'NOT' in s: return False
        if 'DONE' in s: return True  # Covers "BMD DONE", "hrpqct done"
        if 'YES' in s: return True
        if s == 'Y': return True
        if 'PRESENT' in s: return True
        return False

    def is_osteopenia(val):
        return 'OSTEOPENIA' in str(val).upper()

    def is_diabetes(row):
        # Checks both DM columns for safety (DM Status or Type 2 DM columns)
        val_dm = str(row.get(col_dm, '')).upper()
        val_t2 = str(row.get(col_t2dm, '')).upper()

        # Check for various positive indicators
        if 'YES' in val_dm or val_dm.strip() == 'Y' or 'PRESENT' in val_dm: return True
        if 'YES' in val_t2 or val_t2.strip() == 'Y': return True
        return False

    # --- 3. APPLY FILTERS ---
    # Total Cohort = HR-pQCT Done + BMD Done (Strict Inclusion)
    if col_hrpqct in df.columns and col_bmd in df.columns:
        mask_hrpqct = df[col_hrpqct].apply(is_positive)
        mask_bmd = df[col_bmd].apply(is_positive)
        total_cohort = df[mask_hrpqct & mask_bmd].copy()
    else:
        print("⚠️ Warning: Critical inclusion columns not found. Using full dataset.")
        total_cohort = df.copy()

    print(f"✅ Total Cohort Created: N={len(total_cohort)}")

    # Sub-cohorts derived from Total Cohort
    mask_osteo = total_cohort[col_who].apply(is_osteopenia)
    mask_dm = total_cohort.apply(is_diabetes, axis=1)

    cohort_osteopenia = total_cohort[mask_osteo].copy()
    cohort_diabetes = total_cohort[mask_dm].copy()
    cohort_osteo_diabetes = total_cohort[mask_osteo & mask_dm].copy()

    print(f"  - Osteopenic Cohort: N={len(cohort_osteopenia)}")
    print(f"  - Diabetes Cohort: N={len(cohort_diabetes)}")
    print(f"  - Osteopenic + Diabetes: N={len(cohort_osteo_diabetes)}")

    # --- 4. SAVE FILES ---
    # We save the full dataset to ensure all risk factors (Steroids, Falls, History) are available
    files = {
        'cohort_risk_total.csv': total_cohort,
        'cohort_risk_osteopenia.csv': cohort_osteopenia,
        'cohort_risk_diabetes.csv': cohort_diabetes,
        'cohort_risk_osteo_diabetes.csv': cohort_osteo_diabetes
    }

    for name, data in files.items():
        save_path = os.path.join(output_dir, name)
        data.to_csv(save_path, index=False)
        print(f"💾 Saved: {save_path}")


if __name__ == "__main__":
    generate_risk_subcohorts()