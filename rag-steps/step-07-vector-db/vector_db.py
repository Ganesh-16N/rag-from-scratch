import os
import sys

# Step 7: store all the embedded chunks somewhere we can actually search.
# going with chromadb for now since it just runs locally, no server to set up

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-02-data-ingestion"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-03-data-cleaning"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-04-chunking"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-05-metadata"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "step-06-embeddings"))
from data_ingestion import ingest_all
from data_cleaning import clean_docs
from chunking import chunk_docs
from metadata import enrich_all
from embeddings import embed_chunks

try:
    import chromadb
except ImportError:
    chromadb = None
    print("chromadb not installed, can't store anything yet")

DB_DIR = "data/chroma"
COLLECTION_NAME = "rag_chunks"


def get_client():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    return chromadb.PersistentClient(path=DB_DIR)


def upsert_chunks(chunks):
    if chromadb is None:
        return None

    client = get_client()
    collection = client.get_or_create_collection(COLLECTION_NAME)

    ids, embeddings, documents, metadatas = [], [], [], []

    for i, c in enumerate(chunks):
        if "embedding" not in c:
            continue  # skip anything that failed to embed

        ids.append(f"{c['url']}::{c['chunk_index']}::{i}")
        embeddings.append(c["embedding"])
        documents.append(c["text"])

        meta = dict(c.get("meta", {}))
        meta["url"] = c["url"]
        # chroma metadata can't hold lists, so just join this into a string
        if "top_words" in meta:
            meta["top_words"] = ", ".join(meta["top_words"])
        metadatas.append(meta)

    collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    print(f"stored {len(ids)} chunks in the vector db")
    return collection


def search(query_embedding, top_k=5):
    client = get_client()
    collection = client.get_or_create_collection(COLLECTION_NAME)
    return collection.query(query_embeddings=[query_embedding], n_results=top_k)


if __name__ == "__main__":
    docs = clean_docs(ingest_all())
    chunks = chunk_docs(docs)
    chunks = enrich_all(chunks)
    chunks = embed_chunks(chunks)

    upsert_chunks(chunks)

    # quick sanity check - search using a chunk's own vector, it should
    # come back as the closest match to itself
    if chunks and "embedding" in chunks[0]:
        results = search(chunks[0]["embedding"], top_k=3)
        print("sanity check results:", results["ids"])
