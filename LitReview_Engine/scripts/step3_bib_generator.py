import pandas as pd
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


def export_to_bibtex(input_csv, output_bib):
    df = pd.read_csv(input_csv)
    db = BibDatabase()

    entries = []
    for index, row in df.iterrows():
        # Create a unique Citation Key (AuthorYear)
        author_last = str(row['Authors']).split(',')[0].split(' ')[-1].lower()
        year = str(int(row['Year'])) if pd.notna(row['Year']) else "0000"
        cite_key = f"{author_last}{year}"

        entry = {
            'ENTRYTYPE': 'article',
            'ID': cite_key,
            'title': str(row['Title']),
            'author': str(row['Authors']),
            'year': year,
            'abstract': str(row['Abstract']),
            'url': str(row['URL'])
        }
        entries.append(entry)

    db.entries = entries

    writer = BibTexWriter()
    with open(output_bib, 'w') as bibfile:
        bibfile.write(writer.write(db))

    print(f"✅ Successfully exported {len(entries)} papers to {output_bib}")


if __name__ == "__main__":
    export_to_bibtex("../output/02_scored_papers.csv", "../output/final_import.bib")