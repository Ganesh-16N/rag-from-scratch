import os
import sys
from datetime import datetime

# Step 5: attach some basic info to each chunk so later i can filter
# ("only search stuff from this url") instead of relying on similarity alone

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-02-data-ingestion"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-03-data-cleaning"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-04-chunking"))
from data_ingestion import ingest_all
from data_cleaning import clean_docs
from chunking import chunk_docs

STOPWORDS = {"the", "a", "an", "and", "or", "is", "are", "of", "to",
             "in", "for", "on", "it", "this", "that", "with", "as"}


def guess_keywords(text, n=3):
    # very rough keyword guesser - just counts words and takes the
    # most frequent ones, skipping short/common words. not real NLP,
    # but good enough to eyeball what a chunk is about
    words = [w.strip(".,()[]\"'").lower() for w in text.split()]
    counts = {}
    for w in words:
        if len(w) < 4 or w in STOPWORDS:
            continue
        counts[w] = counts.get(w, 0) + 1

    top = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:n]
    return [word for word, _ in top]


def enrich_chunk(chunk):
    text = chunk["text"]
    chunk["meta"] = {
        "url": chunk["url"],
        "chunk_index": chunk["chunk_index"],
        "char_len": len(text),
        "word_count": len(text.split()),
        "added_at": str(datetime.now()),
        "top_words": guess_keywords(text),
        # TODO: language detection would be nice here, look into fasttext later
        # TODO: no access-control stuff yet, this is just a personal project for now
    }
    return chunk


def enrich_all(chunks):
    return [enrich_chunk(c) for c in chunks]


if __name__ == "__main__":
    docs = clean_docs(ingest_all())
    chunks = chunk_docs(docs)
    chunks = enrich_all(chunks)

    print(f"enriched {len(chunks)} chunks")
    for c in chunks[:5]:
        print(c["meta"])
