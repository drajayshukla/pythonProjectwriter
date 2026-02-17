import pandas as pd
import numpy as np
from scipy import stats
import os


def generate_table2_hrpqct():
    # --- 1. ROBUST FILE SEARCH ---
    filename = 'cohort_total_n215.csv'
    data_path = None

    # Search in current directory and subdirectories
    for root, dirs, files in os.walk('.'):
        if filename in files:
            data_path = os.path.join(root, filename)
            print(f"✅ Found data file at: {data_path}")
            break

    # Fallback: Check common relative paths if not found by walk
    if data_path is None:
        potential_paths = [
            'data/03_final/cohort_total_n215.csv',
            '../data/03_final/cohort_total_n215.csv',
            'cohort_total_n215.csv'
        ]
        for p in potential_paths:
            if os.path.exists(p):
                data_path = p
                print(f"✅ Found data file at: {data_path}")
                break

    if data_path is None:
        print(f"❌ Error: Could not find '{filename}'. Please ensure it is in the project directory.")
        return

    # --- 2. LOAD AND PROCESS DATA ---
    df = pd.read_csv(data_path)

    # Define Subgroups
    # Co: Non-DM, Group B (Control)
    # Fx: Non-DM, Group A (Fracture)
    # DM: DM, Group B
    # DMFx: DM, Group A

    def get_group(row):
        # Clean data to ensure string matching works
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

    # --- 3. DEFINE PARAMETERS ---
    # (Friendly Name, Column Name Pattern)
    # {} will be replaced by 'RADIUS' or 'TIBIA'
    params_config = [
        ('Total vBMD (mg HA/cm³)', '{}_ttvBMD'),
        ('Trabecular vBMD (mg HA/cm³)', '{}_tbvBMD'),
        ('Cortical vBMD (mg HA/cm³)', '{}_CTvBMD'),
        ('Trabecular Number (Tb.N, 1/mm)', '{}_TB.N'),
        ('Trabecular Thickness (Tb.Th, mm)', '{}_TB.TH'),
        ('Trabecular Separation (Tb.Sp, mm)', '{}_TB.SP'),
        ('Cortical Thickness (Ct.Th, mm)', '{}_CT.TH'),
        ('Cortical Porosity (Ct.Po, %)', '{}_CT.PO'),
        ('Stiffness (kN/mm)', 'Stiffness_{}'),
        ('Failure Load (F.Load, kN)', 'F.Load_{}')
    ]

    sites = {'Distal Radius': 'RADIUS', 'Distal Tibia': 'TIBIA'}
    results = []

    # --- 4. CALCULATE STATISTICS ---
    for site_name, site_prefix in sites.items():
        # Section Header
        results.append({
            'Parameter': f"--- {site_name} ---",
            'Co': '', 'Fx': '', 'DM': '', 'DMFx': '',
            'p (Co vs Fx)': '', 'p (DM vs DMFx)': ''
        })

        for label, col_pattern in params_config:
            col = col_pattern.format(site_prefix)

            # Check if column exists
            if col not in df.columns:
                continue

            # Get data vectors
            g_co = df[df['Subgroup'] == 'Co'][col].dropna()
            g_fx = df[df['Subgroup'] == 'Fx'][col].dropna()
            g_dm = df[df['Subgroup'] == 'DM'][col].dropna()
            g_dmfx = df[df['Subgroup'] == 'DMFx'][col].dropna()

            # Handle absolute values for FEA (Stiffness/Load are often negative in output)
            if 'Stiffness' in label or 'Load' in label:
                g_co, g_fx, g_dm, g_dmfx = g_co.abs(), g_fx.abs(), g_dm.abs(), g_dmfx.abs()

            # Helper: Format Mean ± SD
            def fmt(s):
                return f"{s.mean():.2f} ± {s.std():.2f}" if len(s) > 0 else "-"

            # Helper: T-Test P-Value
            def get_p(a, b):
                if len(a) > 1 and len(b) > 1:
                    _, p = stats.ttest_ind(a, b, equal_var=False)  # Welch's t-test
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

    # Save to 'results/tables' directory
    output_dir = os.path.join(os.path.dirname(data_path), '..', '..', 'results', 'tables')
    # Or just use local 'results/tables' if simpler:
    # output_dir = 'results/tables'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'Table2_HRpQCT_Parameters.csv')
    final_df.to_csv(output_path, index=False)

    print("\n" + "=" * 80)
    print("GENERATED TABLE 2 (Preview)")
    print("=" * 80)
    print(final_df.to_string(index=False))
    print("\n" + "=" * 80)
    print(f"✅ Table saved successfully to: {output_path}")


if __name__ == "__main__":
    generate_table2_hrpqct()