import pandas as pd
import os


def score_papers(input_csv, output_csv):
    print(f"   -> Loading: {input_csv}")

    # 1. Safety Check: Does file exist?
    if not os.path.exists(input_csv):
        print(f"   ❌ ERROR: Input file not found: {input_csv}")
        return

    df = pd.read_csv(input_csv)

    # --- CRITICAL FIX: Handle Missing Abstracts ---
    # This fixes the "TypeError: can only concatenate str (not 'float')" error
    # We replace NaN (missing values) with empty strings
    df['Title'] = df['Title'].fillna('').astype(str)
    df['Abstract'] = df['Abstract'].fillna('').astype(str)

    # 2. Define Scoring Logic (Tailored for "Grey Zone" & "Diabetes")
    keywords_high_value = ['osteopenia', 't-score', 'diabetes', 'cortical porosity', 'grey zone']
    keywords_medium_value = ['hr-pqct', 'microarchitecture', 'fracture discrimination', 'trabecular', 'vbm', 'auc']

    scores = []
    for index, row in df.iterrows():
        # Combine text for searching (Safe concatenation now)
        text = (row['Title'] + " " + row['Abstract']).lower()
        score = 0

        # A. Keyword Matching
        for word in keywords_high_value:
            if word in text: score += 3
        for word in keywords_medium_value:
            if word in text: score += 1

        # B. Impact Factor Proxy (Citations)
        # Handle case where citations might be missing/NaN
        try:
            citations = float(row.get('Citations', 0))
            if citations > 50: score += 1
        except:
            pass  # Ignore if citation count is malformed

        # C. SAFETY NET: Gold Standards always get top score
        # Checks the 'Note' column created in Step 1
        if 'Note' in row and str(row['Note']).startswith('GOLD'):
            score += 50

        scores.append(score)

    df['Relevance_Score'] = scores

    # 3. Filter and Sort
    # Keep papers with Score >= 3 (matches at least one high-value or 3 medium keywords)
    df_filtered = df[df['Relevance_Score'] >= 3].sort_values(by='Relevance_Score', ascending=False)

    # 4. Save
    df_filtered.to_csv(output_csv, index=False)

    print(f"   ✅ Filtered down to {len(df_filtered)} high-relevance papers.")
    print(f"   -> Saved to: {output_csv}")


if __name__ == "__main__":
    # Test path (adjust as needed for standalone testing)
    score_papers("../output/01_raw_search.csv", "../output/02_scored_papers.csv")