import os
import json

# Step 2: read back everything step 1 downloaded and pull out plain text.
# starting with just html since that's all i'm collecting for now

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    print("heads up: bs4 isn't installed, falling back to raw text")

RAW_DIR = "data/raw"


def load_html(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    if BeautifulSoup is None:
        return raw  # not great, but works for now

    soup = BeautifulSoup(raw, "html.parser")
    # strip out stuff that isn't really "content"
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(separator="\n")


def ingest_all():
    docs = []

    for filename in os.listdir(RAW_DIR):
        if not filename.endswith(".json"):
            continue

        meta_path = os.path.join(RAW_DIR, filename)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        html_path = meta_path.replace(".json", ".html")
        if not os.path.exists(html_path):
            print(f"no html for {filename}, skipping")
            continue

        text = load_html(html_path).strip()

        if len(text) == 0:
            print(f"got nothing out of {html_path}, skipping")
            continue

        docs.append({
            "url": meta["url"],
            "text": text,
        })

    print(f"ingested {len(docs)} docs")
    return docs


if __name__ == "__main__":
    docs = ingest_all()
    for doc in docs:
        print(doc["url"], "-", len(doc["text"]), "chars")
