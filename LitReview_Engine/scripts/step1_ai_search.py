import pandas as pd
from semanticscholar import SemanticScholar
import os

# --- CONFIGURATION ---
OUTPUT_DIR = "../data/02_processed"  # Or "../output" depending on your folder structure
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_gold_standards():
    """
    Manually fetches the specific 'Twin Papers' (Sornay-Rendu & Patsch)
    to ensure they are ALWAYS present in the dataset as anchors.
    """
    sch = SemanticScholar()
    # Exact titles of your Twin Papers
    twins = [
        "Bone Microarchitecture Assessed by HR-pQCT as Predictor of Fracture Risk in Postmenopausal Women: The OFELY Study",
        "Increased Cortical Porosity in Type 2 Diabetic Postmenopausal Women with Fragility Fractures"
    ]

    gold_papers = []
    print("\n🌟 Fetching Gold Standard 'Twin Papers'...")

    for title in twins:
        try:
            # Search for the exact title
            results = sch.search_paper(title, limit=1,
                                       fields=['title', 'abstract', 'year', 'authors', 'citationCount', 'url'])

            if results:
                item = results[0]
                authors = ", ".join([a.name for a in item.authors]) if item.authors else "Unknown"

                gold_papers.append({
                    'Title': item.title,
                    'Year': item.year,
                    'Authors': authors,
                    'Abstract': item.abstract if item.abstract else "Gold Standard Paper (Abstract N/A)",
                    'Citations': item.citationCount,
                    'URL': item.url,
                    'Note': 'GOLD STANDARD TWIN'  # Tag for sorting/identification
                })
                print(f"   -> Found: {item.title[:50]}...")
            else:
                print(f"   -> WARNING: Could not find Twin Paper: {title}")

        except Exception as e:
            print(f"   -> Error fetching {title}: {e}")

    return gold_papers


def search_literature(query, limit=50):
    """
    Searches Semantic Scholar for new literature and merges it with Gold Standards.
    """
    sch = SemanticScholar()
    print(f"\n🔍 AI Searching for new literature: '{query}'...")

    try:
        results = sch.search_paper(query, limit=limit,
                                   fields=['title', 'abstract', 'year', 'authors', 'citationCount', 'url'])
    except Exception as e:
        print(f"Error connecting to Semantic Scholar: {e}")
        return pd.DataFrame()

    new_papers = []
    for item in results:
        # Basic cleanup
        abstract = item.abstract if item.abstract else ""
        authors = ", ".join([a.name for a in item.authors]) if item.authors else "Unknown"

        new_papers.append({
            'Title': item.title,
            'Year': item.year,
            'Authors': authors,
            'Abstract': abstract,
            'Citations': item.citationCount,
            'URL': item.url,
            'Note': 'AI Search Result'
        })

    # --- MERGE: Gold Standards + New Search ---
    gold_data = get_gold_standards()

    # Combine lists
    full_list = gold_data + new_papers

    # Create DataFrame
    df = pd.DataFrame(full_list)

    # Remove duplicates based on Title (keep Gold Standard version if duplicate exists)
    df = df.drop_duplicates(subset=['Title'], keep='first')

    print(f"\n✅ SUCCESS: Found {len(df)} total papers (including {len(gold_data)} Twins).")
    return df


if __name__ == "__main__":
    # Define your search query based on the "Grey Zone" hypothesis
    search_query = "HR-pQCT osteopenia fracture discrimination diabetes"

    # Run the search
    df_results = search_literature(search_query, limit=50)

    # Save to CSV
    output_file = os.path.join(OUTPUT_DIR, "01_raw_search.csv")
    df_results.to_csv(output_file, index=False)
    print(f"📄 Results saved to: {output_file}")