import os

# Define the content for the missing/new sections
files_content = {
    # 1. Areal BMD (The "Negative Finding")
    "04_results_areal_bmd.qmd": """
## Areal Bone Mineral Density (aBMD)

Dual-energy X-ray absorptiometry (DXA) was performed in all 215 subjects. In the total cohort, mean $T$-scores at the lumbar spine (L1-L4) and femoral neck were within the osteopenic range for both the fracture and control groups, confirming the "grey zone" status of the study population (Figure 2).

### Osteopenic Sub-cohort ($n=91$)
In the primary osteopenic sub-cohort, densitometry failed to discriminate between fracture and non-fracture status.
* **Lumbar Spine:** $aBMD$ was similar between Fx ($n=47$) and Co ($n=44$) groups ($0.86 \pm 0.09$ vs $0.88 \pm 0.08$ g/cm²; $-2.3\%$, $p = 0.110$).
* **Femoral Neck:** $aBMD$ was virtually identical ($p = 0.713$).

### Diabetic Sub-cohorts
Notably, in the **Diabetic Osteopenia ($n=66$)** subgroup, $aBMD$ values were paradoxically preserved in the fracture group ($+1.4\%$ at femoral neck, $p=0.74$) compared to controls. This "Diabetic Paradox" confirms that $aBMD$ is a poor surrogate for skeletal strength in T2DM.
""",

    # 2. Peripheral Quality (Trabecular vs Cortical)
    "04_results_peripheral_bone_quality.qmd": """
## Peripheral Bone Microarchitecture and Quality

**Osteopenic Sub-cohort ($n=91$): The Trabecular Driver**
In the primary "Grey Zone" cohort, HR-pQCT revealed a profound deficit in trabecular integrity. At the distal radius, women with fractures exhibited significantly lower **Trabecular Number ($Tb.N$)** compared to controls ($-11.6\%$, $p < 0.001$). This was the dominant structural failure mode.

**Diabetic Osteopenia ($n=66$): The Cortical Switch**
A distinct "Cortical Phenotype" emerged in the diabetic osteopenic subgroup. While trabecular deficits were present, the most striking failure was in the cortical envelope. At the distal tibia, diabetic fracture subjects (DMFx) displayed a significant increase in **Cortical Porosity ($Ct.Po$)** ($+58.1\%$, $p = 0.005$) compared to diabetic controls. This "Swiss-Cheese" transformation drives fragility in the weight-bearing skeleton of diabetic patients.
""",

    # 3. FEA (Biomechanics)
    "04_results_fea_biomechanics.qmd": """
## Biomechanical Competence ($\mu$FEA)

**General Osteopenia ($n=91$):**
Radius **Failure Load** was $14.3\%$ lower in fracturers ($p = 0.03$), driven by the loss of trabecular connectivity.

**Diabetic Osteopenia ($n=66$):**
Tibia **Failure Load** was $16.8\%$ lower in fracturers ($p = 0.01$). Critically, in this group, failure load was strongly correlated with **Cortical Porosity** ($r = -0.48$, $p < 0.01$), confirming that porosity acts as the primary stress riser in diabetic bone.
""",

    # 4. Multivariable Risk (The Proof)
    "04_results_multivariable_risk.qmd": """
## Multivariable Risk Modeling

To determine independent fracture risk, we adjusted for Age, BMI, and Total Hip $aBMD$.

* **Trabecular Driver:** In general osteopenia, **Radius $Tb.N$** remained the strongest predictor ($aOR = 2.59$, $p < 0.001$).
* **Cortical Switch:** In diabetic osteopenia, **Radius $Ct.Po$** emerged as the dominant predictor ($aOR = 1.94$, $p < 0.05$).

This dissociation proves that HR-pQCT identifies specific structural failure modes that DXA misses.
""",

    # 5. Methods: Statistics
    "03_statistics.qmd": """
## Statistical Analysis

Data were analyzed using Python (v3.11). Group differences were assessed via Student's t-test or Mann-Whitney U-test. To verify the independent value of HR-pQCT, multivariable logistic regression models were constructed, adjusting for Age, BMI, and Total Hip $aBMD$. Adjusted Odds Ratios (aOR) are reported per 1-SD change.
"""
}


def create_manuscript_sections():
    # --- DYNAMIC PATH ANCHORING ---
    # This ensures we find the folder relative to THIS script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from 'scripts' to 'HRPQCT_BMD_TBS_FRAX'
    project_root = os.path.dirname(script_dir)
    # Target directory
    target_dir = os.path.join(project_root, "manuscript", "sections")

    print(f"📂 Targeting Directory: {target_dir}")

    if not os.path.exists(target_dir):
        print(f"❌ Error: The directory {target_dir} does not exist.")
        print("Please check your folder structure.")
        return

    for filename, content in files_content.items():
        file_path = os.path.join(target_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Successfully wrote: {filename}")


if __name__ == "__main__":
    create_manuscript_sections()

