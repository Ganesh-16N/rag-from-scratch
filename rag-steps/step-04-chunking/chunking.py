import os
import sys

# Step 4: cut the cleaned text into smaller pieces (chunks) so the LLM
# doesn't have to read a whole document just to answer one question.
# each chunk should be small enough to embed but still make sense on its own

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-02-data-ingestion"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-03-data-cleaning"))
from data_ingestion import ingest_all
from data_cleaning import clean_docs

# just picked these numbers, no real science behind them yet.
# might come back and tune once i see how retrieval does
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    # try to cut on paragraph breaks so we don't split an idea in half.
    # falls back to raw slicing if a single paragraph is bigger than size
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) < size:
            current += para + "\n\n"
            continue

        if current:
            chunks.append(current.strip())
            current = ""

        if len(para) > size:
            # paragraph is too big on its own, just slice it up with overlap
            start = 0
            while start < len(para):
                chunks.append(para[start:start + size])
                start += size - overlap
        else:
            current = para + "\n\n"

    if current.strip():
        chunks.append(current.strip())

    return chunks


def chunk_doc(doc):
    pieces = chunk_text(doc["text"])
    return [
        {"url": doc["url"], "chunk_index": i, "text": piece}
        for i, piece in enumerate(pieces)
    ]


def chunk_docs(docs):
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_doc(doc))
    return all_chunks


if __name__ == "__main__":
    docs = clean_docs(ingest_all())
    chunks = chunk_docs(docs)

    print(f"got {len(chunks)} chunks from {len(docs)} docs")
    for c in chunks[:5]:
        print(c["url"], "chunk", c["chunk_index"], "-", len(c["text"]), "chars")
