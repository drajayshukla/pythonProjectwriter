import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from scipy import stats


def generate_dxa_boxplot():
    # Dynamic Path Anchoring
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_path = os.path.join(project_root, 'data', '03_final', 'cohort_total_n215.csv')
    output_dir = os.path.join(project_root, 'results', 'figures')
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(data_path):
        print(f"File not found: {data_path}")
        return

    df = pd.read_csv(data_path)

    # 1. Define Subgroups (Co, Fx, DM, DMFx)
    # Logic:
    # DM = 'Y' & Group B -> 'DM' (Diabetic Control)
    # DM = 'Y' & Group A -> 'DMFx' (Diabetic Fracture)
    # DM = 'N' & Group B -> 'Co' (Non-Diabetic Control)
    # DM = 'N' & Group A -> 'Fx' (Non-Diabetic Fracture)

    def classify_group(row):
        is_dm = row['TYPE 2 DM'] == 'Y'
        is_fx = row['GROUP'] == 'Group A'

        if is_dm and is_fx: return 'DMFx'
        if is_dm and not is_fx: return 'DM'
        if not is_dm and is_fx: return 'Fx'
        return 'Co'

    df['Study_Group'] = df.apply(classify_group, axis=1)

    # Order for plotting
    order = ['Co', 'Fx', 'DM', 'DMFx']

    # 2. Select DXA Variables (T-Scores)
    # Adjust column names to match your CSV
    dxa_vars = {
        'L1-L4 T SCORE': 'Lumbar Spine (L1-L4)',
        'NECK_TSCORE': 'Femoral Neck',
        'HT_TSCORE': 'Total Hip'
    }

    # 3. Plotting
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    for ax, (col, title) in zip(axes, dxa_vars.items()):
        if col not in df.columns: continue

        # Create Boxplot
        sns.boxplot(x='Study_Group', y=col, data=df, order=order, ax=ax,
                    palette=['#e0e0e0', '#4d4d4d', '#b3cde3', '#005a32'],  # Grayscale/Blue-Green scheme
                    width=0.6, linewidth=1.5, fliersize=3)

        # Add Swarmplot for individual points
        sns.stripplot(x='Study_Group', y=col, data=df, order=order, ax=ax,
                      color='black', alpha=0.4, size=3, jitter=True)

        # Add Diagnostic Threshold Line (-2.5)
        ax.axhline(y=-2.5, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.text(3.5, -2.4, 'Osteoporosis (-2.5)', color='red', fontsize=9, ha='right')

        # Formatting
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('T-Score' if ax == axes[0] else '')
        ax.tick_params(axis='x', labelsize=12)

        # Statistical Annotation (Optional - Simple T-Test)
        # Compare Co vs Fx and DM vs DMFx
        for i, pair in enumerate([('Co', 'Fx'), ('DM', 'DMFx')]):
            g1 = df[df['Study_Group'] == pair[0]][col].dropna()
            g2 = df[df['Study_Group'] == pair[1]][col].dropna()
            if len(g1) > 2 and len(g2) > 2:
                t, p = stats.ttest_ind(g1, g2)
                if p < 0.05:
                    # Draw significance bar
                    y_max = max(g1.max(), g2.max()) + 0.5
                    x1, x2 = (0, 1) if i == 0 else (2, 3)
                    ax.plot([x1, x1, x2, x2], [y_max, y_max + 0.2, y_max + 0.2, y_max], lw=1, c='k')
                    ax.text((x1 + x2) * .5, y_max + 0.25, "*", ha='center', va='bottom', color='k')

    plt.tight_layout()
    save_path = os.path.join(output_dir, 'Figure2_DXA_Boxplots.png')
    plt.savefig(save_path, dpi=300)
    print(f"✅ Figure saved to: {save_path}")
    plt.show()


if __name__ == "__main__":
    generate_dxa_boxplot()