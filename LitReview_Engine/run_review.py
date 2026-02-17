import sys
import os

# Ensure Python sees the 'scripts' folder as a package
sys.path.append(os.path.join(os.getcwd(), 'scripts'))

# Import your renamed modules
import step1_ai_search as step1
import step2_relevance_scorer as step2
import step3_bib_generator as step3
import step4_bib_check as step4


def main():
    print("🚀 STARTING LIT REVIEW ENGINE...")

    # --- CONFIGURATION ---
    # The specific query for your "Grey Zone" & "Diabetes" paper
    QUERY = "HR-pQCT osteopenia fracture discrimination diabetes"

    # File Paths (Relative to this script)
    FILE_RAW = "output/01_raw_search.csv"
    FILE_SCORED = "output/02_scored_papers.csv"
    FILE_BIB = "output/final_import.bib"

    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)

    # --- STEP 1: AI SEARCH ---
    print("\n--- 1. AI SEARCH (Semantic Scholar) ---")
    # This fetches Sornay-Rendu & Patsch FIRST, then searches for others
    df = step1.search_literature(QUERY, limit=50)
    df.to_csv(FILE_RAW, index=False)
    print(f"📄 Saved raw search to: {FILE_RAW}")

    # --- STEP 2: SCORING ---
    print("\n--- 2. RELEVANCE SCORING ---")
    # Filters based on keywords like 'cortical porosity' and 'AUC'
    step2.score_papers(FILE_RAW, FILE_SCORED)

    # --- STEP 3: BIBTEX GENERATION ---
    print("\n--- 3. GENERATING ZOTERO IMPORT FILE ---")
    # Converts the scored CSV into a .bib file
    step3.export_to_bibtex(FILE_SCORED, FILE_BIB)

    # --- STEP 4: AUDIT (The "Expert Check") ---
    print("\n--- 4. FINAL INTEGRITY AUDIT ---")
    # Verifies that Sornay-Rendu and Patsch are actually in the file
    step4.audit_references(FILE_BIB)

    print("\n🎉 DONE! The file 'output/final_import.bib' is ready for Zotero.")


if __name__ == "__main__":
    main()