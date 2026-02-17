import bibtexparser
import sys


def audit_references(bib_file):
    print(f"--- AUDITING BIBLIOGRAPHY: {bib_file} ---")

    try:
        with open(bib_file) as f:
            bib_database = bibtexparser.load(f)
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Bibliography file not found at {bib_file}")
        return

    # 1. Get all Citation Keys
    keys = [entry.get('ID', '').lower() for entry in bib_database.entries]
    titles = [entry.get('title', '').lower() for entry in bib_database.entries]

    print(f"Total References Found: {len(keys)}")

    # 2. THE TWIN PAPER CHECK (Mandatory for JBMR Submission)
    twins = {
        'sornay-rendu': {
            'year': '2017',
            'fragment': 'ofely study',
            'role': 'Primary Template (Osteopenia)'
        },
        'patsch': {
            'year': '2013',
            'fragment': 'cortical porosity',
            'role': 'Secondary Template (Diabetes)'
        }
    }

    missing_twins = []

    for key, info in twins.items():
        # check if key exists (e.g., sornay-rendu2017) OR if title exists in DB
        key_match = any(key in k and info['year'] in k for k in keys)
        title_match = any(info['fragment'] in t for t in titles)

        if key_match or title_match:
            print(f"✅ CONFIRMED: {info['role']} is present.")
        else:
            print(f"❌ MISSING: {info['role']} ({key} et al. {info['year']})")
            missing_twins.append(key)

    if missing_twins:
        print("\n⚠️  ACTION REQUIRED: You are missing the 'Twin Papers'.")
        print("    Please add Sornay-Rendu (2017) and Patsch (2013) to Zotero immediately.")
        print("    Your paper needs these to pass the 'Expert Reviewer' check.")
    else:
        print("\n🏆 Bibliography aligns with JBMR Gold Standards.")


if __name__ == "__main__":
    # Adjust path if necessary
    audit_references("../manuscript/references.bib")