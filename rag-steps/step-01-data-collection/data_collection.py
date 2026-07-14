# Step 1 - Data Collection
# Before we can build anything, we need raw material.
# This script fetches web pages and saves them locally along with a small
# manifest file that tracks where each page came from and when we grabbed it.

import hashlib
import json
import requests
from datetime import datetime
from pathlib import Path


RAW_DIR = Path("data/raw")


def collect_url(url: str, raw_dir: Path = RAW_DIR) -> dict:
    """Fetch a URL and write the HTML + a manifest file to raw_dir."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    body = resp.text
    content_hash = hashlib.sha256(body.encode()).hexdigest()

    manifest = {
        "source": "web",
        "uri": url,
        "fetched_at": datetime.utcnow().isoformat(),
        "etag": resp.headers.get("ETag"),
        "content_hash": content_hash,
        "status_code": resp.status_code,
    }

    raw_dir.mkdir(parents=True, exist_ok=True)

    (raw_dir / f"{content_hash}.html").write_text(body, encoding="utf-8")
    (raw_dir / f"{content_hash}.manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    return manifest
