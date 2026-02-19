import os

base_dir = "/Users/dr.ajayshukla/PycharmProjects/pythonProjectwriter/THYROIDPET_case report"

# 1. BIBLIOGRAPHY (Updated Pruthi pages and Ross citation)
content_bib = """@article{soelberg2012,
  title = {Risk of Malignancy in Thyroid Incidentalomas Detected by 18F-fluorodeoxyglucose Positron Emission Tomography: A Systematic Review},
  author = {Soelberg, KK and Bonnema, SJ and Brix, TH and Hegedüs, L},
  year = {2012},
  journal = {Thyroid},
  volume = {22},
  number = {9},
  pages = {918--925}
}

@article{amino1981,
  title = {Serum Ratio of Triiodothyronine to Thyroxine, and Thyroxine-Binding Globulin and Calcitonin Concentrations in Graves' Disease and Destruction-Induced Thyrotoxicosis},
  author = {Amino, N and Yabu, Y and Miki, T and others},
  year = {1981},
  journal = {J Clin Endocrinol Metab},
  volume = {53},
  number = {1},
  pages = {113--116}
}

@article{ross2016,
  title = {2016 American Thyroid Association Guidelines for Diagnosis and Management of Hyperthyroidism and Other Causes of Thyrotoxicosis},
  author = {Ross, DS and Burch, HB and Cooper, DS and others},
  year = {2016},
  journal = {Thyroid},
  volume = {26},
  number = {10},
  pages = {1343--1421}
}

@article{chin2004,
  title = {Recombinant Human Thyrotropin Stimulation of Fluoro-D-glucose Positron Emission Tomography Uptake in Well-Differentiated Thyroid Carcinoma},
  author = {Chin, BB and Patel, P and Cohade, C and others},
  year = {2004},
  journal = {J Clin Endocrinol Metab},
  volume = {89},
  number = {1},
  pages = {91--95}
}

@article{haber1997,
  title = {GLUT1 Glucose Transporter Expression in Benign and Malignant Thyroid Nodules},
  author = {Haber, RS and Weiser, KR and Pritsker, A and others},
  year = {1997},
  journal = {Thyroid},
  volume = {7},
  number = {3},
  pages = {363--367}
}

@article{pruthi2015,
  title = {Does the Intensity of Diffuse Thyroid Gland Uptake on F-18 FDG PET/CT Predict the Severity of Hypothyroidism?},
  author = {Pruthi, A and Choudhury, PS and Gupta, M and others},
  year = {2015},
  journal = {Indian J Nucl Med},
  volume = {30},
  number = {1},
  pages = {16--20}
}

@article{karantanis2007,
  title = {Clinical Significance of Diffusely Increased 18F-FDG Uptake in the Thyroid Gland},
  author = {Karantanis, D and Bogsrud, TV and Wiseman, GA and others},
  year = {2007},
  journal = {J Nucl Med},
  volume = {48},
  number = {6},
  pages = {896--901}
}

@article{kim2019,
  title = {Diffusely Increased 18F-FDG Uptake in the Thyroid Gland and Risk of Thyroid Dysfunction},
  author = {Kim, YH and Chang, Y and Kim, Y and others},
  year = {2019},
  journal = {J Clin Med},
  volume = {8},
  number = {4},
  pages = {443}
}
"""

# 2. BLINDED MANUSCRIPT (.qmd)
content_article = """---
format:
  docx:
    toc: false
    mainfont: "Times New Roman"
    fontsize: 14pt
bibliography: thyreferfinal.bib
csl: vancouver.csl
---

# Letter to the Editor

**Title:** Intense Diffuse Thyroid FDG Uptake (SUVmax 14.0) Mimicking Malignancy in Severe Radiation-Induced Hypothyroidism

**Abstract:** Incidental thyroid uptake on 18F-FDG PET/CT is a common diagnostic challenge. While focal uptake warrants further detailed workup due to malignancy risk, diffuse uptake is typically associated with benign autoimmunity. We report a 51-year-old post-radiation patient who presented with an SUVmax of 14.0—an intensity suspicious for primary thyroid lymphoma or anaplastic malignancy—but was found to have profound hypothyroidism (TSH > 100 uIU/mL). Review of her history revealed the inadvertent use of Propylthiouracil (PTU) for radiation-induced thyroiditis. High-resolution ultrasound confirmed a structurally benign gland, avoiding unnecessary biopsy. Profound TSH elevation likely induced GLUT-1 transporter upregulation on follicular cell membranes, creating a functional metabolic 'overdrive' despite a structurally normal gland. This case highlights that TSH stimulation alone can drive FDG avidity to levels mimicking malignancy.

**Keywords:** FDG PET/CT, Hypothyroidism, Radiation Thyroiditis, Incidentaloma.

**Introduction:** Thyroid incidentalomas are detected in 1-2% of PET/CT scans. Clinical differentiation relies heavily on the pattern of uptake: focal lesions carry a malignancy risk of approximately 35%, whereas diffuse uptake is generally benign (~4%) [@soelberg2012]. However, diagnostic uncertainty arises when the Standardized Uptake Value (SUVmax) exceeds 10, as this high metabolic intensity is a recognized hallmark of primary thyroid lymphoma and anaplastic thyroid carcinoma, frequently overlapping with the upper limits of benign inflammatory or functional states.

**Case Report:** A 51-year-old female presented in February 2026 with fatigue and weight gain. She had completed surgery and radiotherapy for carcinoma of the buccal mucosa one year prior (February 2025). 

Review of records from an outside facility showed she had been treated with Propylthiouracil (PTU) 100 mg BD for presumed hyperthyroidism. The initial thyroid function tests (TFTs) post-radiation showed a **TSH < 0.0001 uIU/mL**, **Total T4 30 ug/dL** (4.5–12.0), and **Total T3 212 ng/dL** (80–200). In retrospect, the **T3/T4 ratio was 7.0** (212/30), which is consistent with destructive thyroiditis rather than Graves’ disease [@amino1981]. The initiation of PTU, indicated only for hyperthyroidism (synthesis) and not destructive thyrotoxicosis [@ross2016], likely blocked recovery and accelerated the progression to hypothyroidism. PTU was discontinued 6 months ago.

Current evaluation revealed profound hypothyroidism: **TSH > 100 uIU/mL**, **Total T4 0.97 ug/dL**, and **Total T3 0.2 ng/dL**. TSH Receptor Antibodies were negative. A surveillance PET/CT showed intense, symmetric diffuse uptake in the thyroid with an **SUVmax of 14.0**. High-resolution ultrasound showed a gland of preserved volume with heterogeneous echotexture but no focal nodules. Biopsy was deferred, and Levothyroxine was initiated.

**Discussion:** The magnitude of FDG uptake in this case (SUVmax 14.0) is the primary diagnostic confounder. While diffuse thyroidal FDG avidity is a characteristic feature of autoimmune thyroiditis, values exceeding 10.0 are statistically rare in benign disease and clinically necessitate the exclusion of high-grade malignancy.

The mechanism here is physiological. TSH stimulates glucose uptake in thyroid follicular cells by upregulating GLUT-1 transporters [@chin2004; @haber1997]. In this patient, the “double hit” of radiation damage and PTU-induced blockade resulted in uninhibited TSH secretion (>100), driving thyrocytes to maximal metabolic capacity.

Pruthi et al. identified that over 84% of patients with incidental diffuse thyroid FDG uptake have underlying thyroid dysfunction [@pruthi2015]. While they found no linear correlation between absolute TSH levels and SUVmax, their findings establish diffuse avidity as a strong clinical indicator of hypothyroidism, justifying biochemical evaluation over immediate biopsy.

In radiation-induced thyroiditis, TSH suppression typically attenuates the functional component of FDG avidity; however, the metabolic signal may remain elevated due to chronic actinic inflammation and tissue remodeling. Provided the ultrasound confirms a structurally benign gland without focal masses, a persistent metabolic signal should be managed with clinical surveillance rather than immediate intervention, as radiation-damaged thyrocytes may remain hypermetabolic long after biochemical euthyroidism is achieved [@karantanis2007].

**Conclusion:** Severe elevation of TSH can produce thyroid FDG avidity (SUVmax > 10) that mimics high-grade malignancy. Clinicians should correlate PET findings with thyroid function tests and ultrasound morphology to avoid unnecessary invasive procedures [@kim2019].

**Figure Legend:** **Figure 1:** (A) Coronal fused PET/CT showing intense diffuse FDG uptake (SUVmax 14.0). (B) High-resolution ultrasound showing preserved thyroid volume without focal nodularity.
"""

# 3. WRITE TO FILES
files = {
    "thyreferfinal.bib": content_bib,
    "Article_Final.qmd": content_article
}

for filename, content in files.items():
    file_path = os.path.join(base_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {filename}")

print("\nFinal logical manuscript created. Run:")
print("quarto render Article_Final.qmd --to docx")