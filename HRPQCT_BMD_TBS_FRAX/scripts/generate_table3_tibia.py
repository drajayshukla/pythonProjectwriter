import pandas as pd
import numpy as np
from scipy import stats
import os


def generate_table3_tibia():
    # --- 1. ROBUST FILE SEARCH ---
    filename = 'cohort_total_n215.csv'
    data_path = None

    # Search in current directory and subdirectories
    for root, dirs, files in os.walk('.'):
        if filename in files:
            data_path = os.path.join(root, filename)
            print(f"✅ Found data file at: {data_path}")
            break

    # Fallback paths
    if data_path is None:
        potential_paths = [
            'data/03_final/cohort_total_n215.csv',
            '../data/03_final/cohort_total_n215.csv'
        ]
        for p in potential_paths:
            if os.path.exists(p):
                data_path = p
                break

    if data_path is None:
        print(f"❌ Error: Could not find '{filename}'.")
        return

    # --- 2. LOAD AND PROCESS DATA ---
    df = pd.read_csv(data_path)

    # Define Subgroups
    # Co: Non-DM, Group B (Control)
    # Fx: Non-DM, Group A (Fracture)
    # DM: DM, Group B
    # DMFx: DM, Group A

    def get_group(row):
        is_dm = str(row.get('TYPE 2 DM', '')).strip().upper() == 'Y'
        is_fx = str(row.get('GROUP', '')).strip() == 'Group A'

        if not is_dm and not is_fx: return 'Co'
        if not is_dm and is_fx: return 'Fx'
        if is_dm and not is_fx: return 'DM'
        if is_dm and is_fx: return 'DMFx'
        return 'Unknown'

    df['Subgroup'] = df.apply(get_group, axis=1)

    # Verify Group Counts
    print("\nPatient Counts per Subgroup:")
    print(df['Subgroup'].value_counts())

    # --- 3. DEFINE TIBIA PARAMETERS ---
    # Only Tibia-specific parameters
    params_config = [
        ('Standard Parameters', None),
        ('Total vBMD (mg HA/cm³)', 'TIBIA_ttvBMD'),
        ('Trabecular vBMD (mg HA/cm³)', 'TIBIA_tbvBMD'),
        ('Cortical vBMD (mg HA/cm³)', 'TIBIA_CTvBMD'),
        ('Trabecular Number (Tb.N, 1/mm)', 'TIBIA_TB.N'),
        ('Trabecular Thickness (Tb.Th, mm)', 'TIBIA_TB.TH'),
        ('Trabecular Separation (Tb.Sp, mm)', 'TIBIA_TB.SP'),
        ('Cortical Thickness (Ct.Th, mm)', 'TIBIA_CT.TH'),
        ('Cortical Structure', None),
        ('Cortical Porosity (Ct.Po, %)', 'TIBIA_CT.PO'),
        # Add Ct.Po.V or relative porosity if available in your columns
        ('Biomechanical Parameters', None),
        ('Stiffness (kN/mm)', 'Stiffness_TIBIA'),
        ('Failure Load (F.Load, kN)', 'F.Load_TIBIA')
    ]

    results = []

    # --- 4. CALCULATE STATISTICS ---
    for label, col in params_config:
        # Handle Section Headers
        if col is None:
            results.append({
                'Parameter': f"--- {label} ---",
                'Co': '', 'Fx': '', 'DM': '', 'DMFx': '',
                'p (Co vs Fx)': '', 'p (DM vs DMFx)': ''
            })
            continue

        # Check if column exists
        if col not in df.columns:
            continue

        # Get data vectors
        g_co = df[df['Subgroup'] == 'Co'][col].dropna()
        g_fx = df[df['Subgroup'] == 'Fx'][col].dropna()
        g_dm = df[df['Subgroup'] == 'DM'][col].dropna()
        g_dmfx = df[df['Subgroup'] == 'DMFx'][col].dropna()

        # Handle absolute values for FEA
        if 'Stiffness' in label or 'Load' in label:
            g_co, g_fx, g_dm, g_dmfx = g_co.abs(), g_fx.abs(), g_dm.abs(), g_dmfx.abs()

        # Helper: Format Mean ± SD
        def fmt(s):
            return f"{s.mean():.2f} ± {s.std():.2f}" if len(s) > 0 else "-"

        # Helper: T-Test P-Value (Welch's)
        def get_p(a, b):
            if len(a) > 1 and len(b) > 1:
                _, p = stats.ttest_ind(a, b, equal_var=False)
                return f"{p:.3f}"
            return "-"

        # Append Row
        results.append({
            'Parameter': label,
            'Co': fmt(g_co),
            'Fx': fmt(g_fx),
            'DM': fmt(g_dm),
            'DMFx': fmt(g_dmfx),
            'p (Co vs Fx)': get_p(g_co, g_fx),
            'p (DM vs DMFx)': get_p(g_dm, g_dmfx)
        })

    # --- 5. EXPORT TABLE ---
    final_df = pd.DataFrame(results)

    # Save
    output_dir = 'results/tables'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'Table3_Tibia_Parameters.csv')
    final_df.to_csv(output_path, index=False)

    print("\n" + "=" * 80)
    print("GENERATED TABLE 3: DISTAL TIBIA (Preview)")
    print("=" * 80)
    print(final_df.to_string(index=False))
    print("\n" + "=" * 80)
    print(f"✅ Table saved successfully to: {output_path}")


if __name__ == "__main__":
    generate_table3_tibia()