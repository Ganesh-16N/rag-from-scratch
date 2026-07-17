import os
import json
import time
import hashlib
import requests
from datetime import datetime

# Step 1: just grab some pages off the web and save them locally.
# nothing fancy here yet, that comes in later steps (cleaning, chunking etc)

RAW_DIR = "data/raw"


def fetch_url(url):
    print(f"fetching: {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def save_page(url, html):
    if not os.path.exists(RAW_DIR):
        os.makedirs(RAW_DIR)

    # using a hash of the content as the filename so if i run this script
    # twice it won't just re-save the same page over and over
    content_hash = hashlib.md5(html.encode("utf-8")).hexdigest()
    html_path = os.path.join(RAW_DIR, content_hash + ".html")

    if os.path.exists(html_path):
        print("already have this one, skipping")
        return

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # keep some basic info about where this came from, might need it later
    meta = {
        "url": url,
        "fetched_at": str(datetime.now()),
        "hash": content_hash,
    }
    meta_path = os.path.join(RAW_DIR, content_hash + ".json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"saved -> {html_path}")


def collect(urls):
    for url in urls:
        html = fetch_url(url)
        save_page(url, html)
        time.sleep(1)  # be nice to the server


if __name__ == "__main__":
    urls = [
        "https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        "https://docs.python.org/3/library/pathlib.html",
    ]

    collect(urls)
