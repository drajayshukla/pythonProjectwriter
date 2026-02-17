import os


def write_final_complete_paper():
    print("🚀 Generating Final Complete 'paper.qmd'...")

    # --- 1. SETUP PATHS ---
    script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(script_path))
    paper_path = os.path.join(project_root, "manuscript", "paper.qmd")

    # --- 2. DEFINE CONTENT ---

    content = r"""---
title: "Trabecular Disconnection and Biomechanical Weakness Drive Fragility in Osteopenic Postmenopausal Women: An HR-pQCT and $\mu$FEA Study"

author:
  - name: Ajay Shukla, MD, DM
    email: dr.ajayshukla@gmail.com
    affiliations:
      - ref: 1
    attributes:
      corresponding: true
  - name: Sushil Gupta, MD, DM
    affiliations:
      - ref: 1

affiliations:
  - id: 1
    name: Max Super Speciality Hospital
    department: Department of Endocrinology
    city: Lucknow
    state: Uttar Pradesh
    country: India

format:
  pdf:
    documentclass: article
    papersize: letter
    number-sections: true
    colorlinks: true
    keep-tex: true
    fig-pos: 'H'
    geometry:
      - top=25mm
      - left=25mm
      - right=25mm
      - bottom=25mm
  docx:
    toc: true
    number-sections: true
  html:
    toc: true
    theme: cosmo

keywords:
  - HR-pQCT
  - Osteopenia
  - Type 2 Diabetes
  - Microarchitecture
  - Finite Element Analysis

bibliography: HRPQCT_BMD.bib
csl: https://raw.githubusercontent.com/citation-style-language/styles/master/journal-of-bone-and-mineral-research.csl
---

{{< include sections/01_abstract.qmd >}}

{{< include sections/02_introduction.qmd >}}

{{< include sections/03_methods.qmd >}}

{{< include sections/03_statistics.qmd >}}

{{< include sections/04_results.qmd >}}

{{< include sections/05_discussion.qmd >}}

# References

::: {#refs}
:::
"""

    # --- 3. WRITE FILE ---
    try:
        os.makedirs(os.path.dirname(paper_path), exist_ok=True)
        with open(paper_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ SUCCESS: Complete 'paper.qmd' written to: {paper_path}")
        print("   - Authors: Ajay Shukla, Sushil Gupta")
        print("   - Affiliation: Max Super Speciality Hospital")
        print("   - CSL: JBMR Style linked")
        print("   - Sections: Abstract -> Discussion fully integrated")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("\n🚀 FINAL STEP: Run 'quarto render manuscript/paper.qmd --to pdf'")


if __name__ == "__main__":
    write_final_complete_paper()