import os
import subprocess


def produce_all_formats():
    print("🚀 Configuring and Generating Manuscript in PDF, Word, and HTML...")

    # --- 1. SETUP PATHS ---
    script_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(script_path))
    paper_path = os.path.join(project_root, "manuscript", "paper.qmd")

    # --- 2. DEFINE UNIVERSAL CONTENT ---
    # This YAML header is "Safe" for all formats (PDF/Word/HTML).
    # It uses single quotes for the title to handle the Greek letter $\mu$.

    content = r"""---
title: 'Trabecular Disconnection and Biomechanical Weakness Drive Fragility in Osteopenic Postmenopausal Women: An HR-pQCT and $\mu$FEA Study'

author:
  - name: Ajay Shukla, MD, DM
    affiliations:
      - ref: 1
    attributes:
      corresponding: true
      email: dr.ajayshukla@gmail.com
  - name: Sushil Gupta, MD, DM
    affiliations:
      - ref: 1

affiliations:
  - id: 1
    name: Department of Endocrinology, Max Super Speciality Hospital, Lucknow, Uttar Pradesh, India

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
    toc: false
    number-sections: true
    highlight-style: github
  html:
    toc: true
    theme: cosmo
    number-sections: true

keywords:
  - HR-pQCT
  - Osteopenia
  - Type 2 Diabetes
  - Microarchitecture
  - Finite Element Analysis

bibliography: HRPQCT_BMD.bib
csl: https://raw.githubusercontent.com/citation-style-language/styles/master/american-medical-association.csl
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
        with open(paper_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ SUCCESS: 'paper.qmd' updated for universal compatibility.")
    except Exception as e:
        print(f"❌ ERROR writing file: {e}")
        return

    # --- 4. RENDER ALL FORMATS ---
    print("\n--- Starting Render Process ---")

    commands = [
        ("PDF", "quarto render manuscript/paper.qmd --to pdf"),
        ("Word", "quarto render manuscript/paper.qmd --to docx"),
        ("HTML", "quarto render manuscript/paper.qmd --to html")
    ]

    for label, cmd in commands:
        print(f"\n...Rendering {label}...")
        try:
            # We run the command using subprocess (works like running in terminal)
            subprocess.run(cmd, shell=True, check=True, cwd=project_root)
            print(f"✅ {label} Generation Complete.")
        except subprocess.CalledProcessError:
            print(f"❌ {label} Generation Failed.")

    print("\n🎉 DONE! Check the 'manuscript/' folder for your files.")


if __name__ == "__main__":
    produce_all_formats()