import spacy
import re
import os
import sys
from textstat import flesch_reading_ease, text_standard

# --- 1. SETUP & MODEL LOADING ---
print("⏳ Loading NLP Model (this may take a moment)...")
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("⚠️  Model 'en_core_web_md' not found.")
    print("   Please run this command in terminal: python -m spacy download en_core_web_md")
    sys.exit(1)


class ManuscriptQualityAuditor:
    def __init__(self, file_path=None, direct_text=None):
        """
        Initialize with either a file path (for your .qmd files)
        or direct text (for testing).
        """
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.text = f.read()
            self.source = file_path
        elif direct_text:
            self.text = direct_text
            self.source = "Direct Text Input"
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

        # Clean text for analysis (remove markdown headers if needed)
        self.doc = nlp(self.text)

    # --- LAYER 1: AI & FILLER DETECTION ---
    def check_ai_writing(self):
        print(f"\n--- 🤖 LAYER 1: AI WRITING CHECK ({self.source}) ---")
        ai_markers = [
            'delve', 'testament', 'leverage', 'underscores', 'pivotal',
            'comprehensive', 'landscape', 'realm', 'tapestry', 'notably',
            'crucial', 'fostering', 'harnessing'
        ]

        found = list(set([word for word in ai_markers if word in self.text.lower()]))

        if found:
            print(f"⚠️  FLAGGED: Found {len(found)} common AI-filler words.")
            print(f"   Avoid: {found}")
            print("   -> Tip: Replace these with specific verbs (e.g., instead of 'underscores', use 'demonstrates').")
        else:
            print("✅ PASSED: No common AI filler words found.")

    # --- LAYER 2: SCIENTIFIC STYLE ---
    def check_scientific_style(self):
        print("\n--- 📝 LAYER 2: SCIENTIFIC STYLE & READABILITY ---")

        # 1. Readability
        score = flesch_reading_ease(self.text)
        grade = text_standard(self.text)
        print(f"   Readability Score: {score:.1f} (Target: 30-50 for high-impact journals)")
        print(f"   Approx. Grade Level: {grade}")

        if score > 60: print("   ⚠️  Warning: Text may be too simple/conversational for JBMR.")
        if score < 20: print("   ⚠️  Warning: Text is very dense. Consider breaking up long sentences.")

        # 2. Passive Voice
        passive_sentences = []
        sentences = list(self.doc.sents)
        for sent in sentences:
            if any(tok.dep_ == "auxpass" for tok in sent):
                passive_sentences.append(sent.text[:60] + "...")

        passive_pct = (len(passive_sentences) / len(sentences)) * 100 if sentences else 0
        print(f"   Passive Voice: {passive_pct:.1f}% ({len(passive_sentences)}/{len(sentences)} sentences)")

        if passive_pct > 30:
            print("   ⚠️  Warning: Excessive Passive Voice (>30%). Use Active Voice.")
            print("      e.g., Change 'It was shown by HR-pQCT...' to 'HR-pQCT demonstrated...'")

    # --- LAYER 3: FACT GROUNDING (The "Hallucination" Check) ---
    def check_fact_grounding(self):
        print("\n--- 🔍 LAYER 3: FACT & DATA GROUNDING ---")
        unsupported_claims = []
        data_driven_claims = 0

        for sent in self.doc.sents:
            text = sent.text.strip()
            if len(text) < 30: continue  # Skip titles/short phrases

            # Logic: If it contains a number/percent, it MUST have a citation, p-value, or 'Table/Figure' ref
            has_number = re.search(r'\d+%|\d+\.\d+', text)
            has_proof = (
                    re.search(r'\(p\s*[<=]\s*\d', text, re.IGNORECASE) or
                    re.search(r'\[@', text) or
                    "Table" in text or "Figure" in text or
                    re.search(r'n\s*=\s*\d+', text, re.IGNORECASE)
            )

            if has_proof:
                data_driven_claims += 1
            elif has_number and not has_proof:
                # Exclude simple years like (2017)
                if not re.search(r'\(\d{4}\)', text):
                    unsupported_claims.append(text[:80] + "...")

        print(f"   ✅ Data-Driven Sentences: {data_driven_claims}")

        if unsupported_claims:
            print("   ⚠️  UNSUPPORTED CLAIMS (Numbers found without p-value, citation, or Figure ref):")
            for claim in unsupported_claims:
                print(f"      ❌ {claim}")
            print("      -> Action: Add (p<0.05) or [@citation] to these sentences.")
        else:
            print("   ✅ PASSED: All numerical claims appear grounded in data.")

    # --- LAYER 4: PLAGIARISM RISK ---
    def check_plagiarism_risk(self):
        print("\n--- 👮 LAYER 4: PLAGIARISM & TWIN PAPER CHECK ---")
        # Phrases from Sornay-Rendu (2017) and Patsch (2013) to avoid copying directly
        risky_phrases = [
            "bone microarchitecture assessed by hr-pqct as predictor",
            "majority of fragility fractures occur in the osteopenic range",
            "independent of areal bone mineral density",
            "cortical porosity in type 2 diabetic postmenopausal women"
        ]

        found_risk = [phrase for phrase in risky_phrases if phrase in self.text.lower()]

        if found_risk:
            print(f"   ⚠️  HIGH SIMILARITY DETECTED (Paraphrase these immediately):")
            for phrase in found_risk:
                print(f"      - '{phrase}'")
        else:
            print("   ✅ PASSED: No direct copy-paste from Twin Papers detected.")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Define the target file (Adjust this path to your specific section)
    # Example: "../manuscript/sections/01_abstract.qmd"
    target_file = "../manuscript/sections/01_abstract.qmd"

    # 2. Fallback for testing if file doesn't exist yet
    sample_text = """
    In the osteopenic cohort, areal BMD failed to distinguish fracture status (p > 0.05). 
    Conversely, HR-pQCT identified a quality defect. According to [@patsch2013], 
    cortical porosity is key. Failure load was significantly lower (-14.3%, p=0.03).
    The landscape of bone research is a testament to this technology.
    """

    if os.path.exists(target_file):
        auditor = ManuscriptQualityAuditor(file_path=target_file)
    else:
        print(f"ℹ️  File '{target_file}' not found. Running on SAMPLE text for demonstration.")
        auditor = ManuscriptQualityAuditor(direct_text=sample_text)

    # 3. Run All Checks
    auditor.check_ai_writing()
    auditor.check_scientific_style()
    auditor.check_fact_grounding()
    auditor.check_plagiarism_risk()