"""
data_collection.py
Week 1-2 deliverable: build the raw document set + metadata.csv log.

Two ways to add documents to the pipeline:

1) register_local_pdfs()
   You've manually downloaded PDFs from FAO / IPCC / ICAR / IMD / MoEFCC
   (most of these sites require a browser/captcha, so manual download is
   normal and expected). Drop the files anywhere on disk, then call this
   to copy them into data/raw/ and log them with source/topic metadata.

2) download_from_urls()
   For sources that expose direct PDF links (no login/captcha), this will
   download automatically. Network access depends on your environment's
   allowed domains — if a domain is blocked, the error is caught and
   logged instead of crashing the run.

Both paths write to the same metadata.csv, so you can mix manual and
automatic collection freely.
"""

import csv
import hashlib
import shutil
from pathlib import Path
from typing import Iterable, Optional

import requests

from config import RAW_DIR, METADATA_CSV

METADATA_FIELDS = ["filename", "title", "source", "topic", "original_path_or_url", "sha256", "size_kb"]


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_existing_hashes() -> set:
    """Read metadata.csv (if it exists) and return the set of sha256 hashes already logged,
    so re-running collection doesn't create duplicate entries."""
    if not METADATA_CSV.exists():
        return set()
    with open(METADATA_CSV, newline="", encoding="utf-8") as f:
        return {row["sha256"] for row in csv.DictReader(f)}


def _append_metadata_rows(rows: list[dict]) -> None:
    file_exists = METADATA_CSV.exists()
    with open(METADATA_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METADATA_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def _guess_document_metadata(filename: str) -> tuple[str, str]:
    """Supply safe default metadata for PDFs placed directly in data/raw/."""
    name = filename.lower()
    if any(marker in name for marker in ("ipcc", "ar5", "ar6", "spm")):
        return "IPCC", "climate science and agricultural impacts"
    if any(marker in name for marker in ("icar", "nicra", "pcrt", "india", "kerala", "assam", "tamil", "odisha", "madhya", "uttar")):
        return "India / ICAR", "climate-resilient agriculture"
    if any(marker in name for marker in ("fao", "i332", "i249", "i018", "i518", "i603", "i639", "i865", "ca", "cb", "cc")):
        return "FAO", "climate adaptation and food security"
    if "world" in name or "136015" in name:
        return "World Bank", "climate-smart agriculture"
    return "Unclassified", "climate adaptation and agriculture"


def register_untracked_raw_pdfs() -> int:
    """Register every unique PDF already present in ``data/raw``.

    This makes drag-and-drop document additions part of the NLP corpus without
    requiring a separate collection command. Existing metadata and exact
    duplicate PDFs are left untouched.
    """
    existing_hashes = _load_existing_hashes()
    new_rows = []

    for pdf_path in sorted(RAW_DIR.glob("*.pdf")):
        file_hash = _sha256_of_file(pdf_path)
        if file_hash in existing_hashes:
            continue

        source, topic = _guess_document_metadata(pdf_path.name)
        new_rows.append({
            "filename": pdf_path.name,
            "title": pdf_path.stem.replace("%20", " ").replace("_", " "),
            "source": source,
            "topic": topic,
            "original_path_or_url": str(pdf_path),
            "sha256": file_hash,
            "size_kb": round(pdf_path.stat().st_size / 1024, 1),
        })
        existing_hashes.add(file_hash)

    if new_rows:
        _append_metadata_rows(new_rows)
        print(f"Registered {len(new_rows)} untracked PDF(s) already in {RAW_DIR}.")
    else:
        print("All PDFs in data/raw are already registered.")
    return len(new_rows)


def register_local_pdfs(source_folder: str, source: str, topic: str, title_prefix: str = "") -> int:
    """
    Copy every PDF found in `source_folder` into data/raw/, and log it in metadata.csv.

    Args:
        source_folder: folder on disk containing PDFs you've already downloaded
        source: e.g. "FAO", "IPCC", "ICAR", "IMD", "MoEFCC"
        topic: e.g. "crop adaptation", "water management", "soil health"
        title_prefix: optional string prepended to each document's title

    Returns:
        number of new documents registered (duplicates are skipped)
    """
    src = Path(source_folder)
    if not src.exists():
        raise FileNotFoundError(f"Source folder not found: {source_folder}")

    existing_hashes = _load_existing_hashes()
    new_rows = []
    registered = 0

    for pdf_path in sorted(src.glob("*.pdf")):
        file_hash = _sha256_of_file(pdf_path)
        if file_hash in existing_hashes:
            print(f"  [skip] already registered: {pdf_path.name}")
            continue

        dest_name = pdf_path.name
        dest_path = RAW_DIR / dest_name
        # avoid overwriting a different file that happens to share a filename
        counter = 1
        while dest_path.exists():
            dest_path = RAW_DIR / f"{pdf_path.stem}_{counter}{pdf_path.suffix}"
            counter += 1

        shutil.copy2(pdf_path, dest_path)

        title = f"{title_prefix}{pdf_path.stem}".strip()
        size_kb = round(dest_path.stat().st_size / 1024, 1)

        new_rows.append({
            "filename": dest_path.name,
            "title": title,
            "source": source,
            "topic": topic,
            "original_path_or_url": str(pdf_path),
            "sha256": file_hash,
            "size_kb": size_kb,
        })
        existing_hashes.add(file_hash)
        registered += 1
        print(f"  [ok]   registered: {dest_path.name}")

    if new_rows:
        _append_metadata_rows(new_rows)

    print(f"register_local_pdfs: {registered} new document(s) added from '{source_folder}'")
    return registered


def download_from_urls(urls: Iterable[str], source: str, topic: str, timeout: int = 30) -> int:
    """
    Download PDFs directly from a list of URLs (works only for sources that serve
    PDFs without login/captcha). Failures are logged and skipped, not fatal.

    Returns:
        number of documents successfully downloaded and registered
    """
    existing_hashes = _load_existing_hashes()
    downloaded = 0

    for url in urls:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  [fail] could not download {url}: {e}")
            continue

        content = resp.content
        if not content.startswith(b"%PDF-"):
            print(f"  [skip] response was not a PDF: {url}")
            continue
        file_hash = hashlib.sha256(content).hexdigest()
        if file_hash in existing_hashes:
            print(f"  [skip] already registered (duplicate content): {url}")
            continue

        filename = url.split("/")[-1] or f"{file_hash[:10]}.pdf"
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        dest_path = RAW_DIR / filename
        counter = 1
        while dest_path.exists():
            dest_path = RAW_DIR / f"{Path(filename).stem}_{counter}.pdf"
            counter += 1

        with open(dest_path, "wb") as f:
            f.write(content)

        row = {
            "filename": dest_path.name,
            "title": Path(filename).stem,
            "source": source,
            "topic": topic,
            "original_path_or_url": url,
            "sha256": file_hash,
            "size_kb": round(len(content) / 1024, 1),
        }
        # Checkpoint after each file: long collections can be interrupted by a
        # slow host, but successful downloads must remain part of the corpus.
        _append_metadata_rows([row])
        existing_hashes.add(file_hash)
        downloaded += 1
        print(f"  [ok]   downloaded: {dest_path.name}")

    print(f"download_from_urls: {downloaded} new document(s) downloaded")
    return downloaded


def collection_summary() -> None:
    """Print a quick summary of what's been collected so far."""
    if not METADATA_CSV.exists():
        print("No documents collected yet.")
        return
    with open(METADATA_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Total documents collected: {len(rows)}")
    by_source = {}
    for row in rows:
        by_source[row["source"]] = by_source.get(row["source"], 0) + 1
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count}")


if __name__ == "__main__":
    # Example usage — replace with your real sources.
    # register_local_pdfs("~/Downloads/fao_reports", source="FAO", topic="crop adaptation")
    collection_summary()
