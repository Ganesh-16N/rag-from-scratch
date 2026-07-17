import re
import os
import sys

# Step 3: clean up the text a bit before we get to chunking.
# just doing whitespace stuff + basic exact-match dedup for now.
# TODO: look into proper near-duplicate detection later once i understand it

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-02-data-ingestion"))
from data_ingestion import ingest_all


def clean_text(text):
    # collapse 3+ blank lines down to 1
    text = re.sub(r"\n{3,}", "\n\n", text)
    # remove trailing spaces at the end of lines
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def clean_docs(docs):
    seen = set()
    cleaned = []

    for doc in docs:
        text = clean_text(doc["text"])

        # super basic dedup - only catches exact duplicates, that's fine for now
        h = hash(text)
        if h in seen:
            print(f"skipping duplicate: {doc['url']}")
            continue
        seen.add(h)

        doc["text"] = text
        cleaned.append(doc)

    return cleaned


if __name__ == "__main__":
    docs = ingest_all()
    docs = clean_docs(docs)

    print(f"{len(docs)} docs left after cleaning")
    for doc in docs:
        print(doc["url"], "-", len(doc["text"]), "chars")
