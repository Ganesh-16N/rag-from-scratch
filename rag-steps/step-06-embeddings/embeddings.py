import os
import sys
import math

# Step 6: turn each chunk's text into a vector (list of numbers) so we can
# later compare chunks by "closeness" instead of exact keyword matching.
# using OpenAI's embedding api for now since it's the easiest way to start

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-02-data-ingestion"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-03-data-cleaning"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-04-chunking"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-05-metadata"))
from data_ingestion import ingest_all
from data_cleaning import clean_docs
from chunking import chunk_docs
from metadata import enrich_all

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("openai package not installed, can't actually embed anything yet")

MODEL = "text-embedding-3-small"

# not 100% sure what the real token limit is for this model, just
# cutting off long chunks at a character count so the api call doesn't fail
MAX_CHARS = 8000


def normalize(vec):
    # so cosine similarity later can just be a dot product
    length = math.sqrt(sum(x * x for x in vec))
    if length == 0:
        return vec
    return [x / length for x in vec]


def embed_chunks(chunks, batch_size=100):
    if OpenAI is None:
        return chunks

    client = OpenAI()
    out = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"][:MAX_CHARS] for c in batch]

        resp = client.embeddings.create(input=texts, model=MODEL)

        for chunk, item in zip(batch, resp.data):
            chunk["embedding"] = normalize(item.embedding)
            chunk["embedding_model"] = MODEL
            out.append(chunk)

    return out


if __name__ == "__main__":
    docs = clean_docs(ingest_all())
    chunks = chunk_docs(docs)
    chunks = enrich_all(chunks)
    chunks = embed_chunks(chunks)

    print(f"embedded {len(chunks)} chunks")
    for c in chunks[:3]:
        vec = c.get("embedding")
        print(c["url"], "-", len(vec) if vec else "no embedding")
