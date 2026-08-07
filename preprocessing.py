"""
preprocessing.py
Week 3 deliverable: Document Preprocessing and Text Extraction.

For every PDF logged in data/raw/metadata.csv:
  1. Extract raw text per page with PyMuPDF (fitz)
  2. Detect and strip repeated headers/footers (lines that appear on
     many pages are boilerplate, not content)
  3. Clean whitespace/line-break noise
  4. Save the cleaned text as JSON (page-level) in data/processed/
  5. Log extraction stats (char count, page count, warnings) to
     logs/preprocessing_log.csv

Output of this stage feeds directly into Week 4 (chunking) — each
processed JSON file already separates text by page, which chunking
will later split further into smaller passages.
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF

from config import (
    RAW_DIR, PROCESSED_DIR, METADATA_CSV, PREPROCESS_LOG,
    MIN_TEXT_LENGTH, REPEATED_LINE_MAX_LEN, REPEATED_LINE_MIN_PAGE_FRACTION,
)


def _load_metadata() -> list[dict]:
    if not METADATA_CSV.exists():
        raise FileNotFoundError(
            "No metadata.csv found — run data_collection.py first to register documents."
        )
    with open(METADATA_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _extract_pages(pdf_path: Path) -> list[str]:
    """Return a list of raw text strings, one per page."""
    pages = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pages.append(page.get_text("text"))
    return pages


def _find_repeated_lines(pages: list[str]) -> set:
    """
    Identify short lines (likely headers/footers/page numbers) that repeat
    across a large fraction of pages. These get stripped in cleaning.
    """
    line_page_counts = Counter()
    for page_text in pages:
        # count each distinct short line once per page (not once per occurrence)
        lines_on_page = {
            line.strip() for line in page_text.split("\n")
            if line.strip() and len(line.strip()) <= REPEATED_LINE_MAX_LEN
        }
        for line in lines_on_page:
            line_page_counts[line] += 1

    if not pages:
        return set()

    threshold = max(2, int(len(pages) * REPEATED_LINE_MIN_PAGE_FRACTION))
    return {line for line, count in line_page_counts.items() if count >= threshold}


def _clean_page_text(text: str, repeated_lines: set) -> str:
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in repeated_lines:
            continue
        # drop lines that are just a page number, e.g. "12" or "Page 12"
        if re.fullmatch(r"(page\s*)?\d+", stripped, flags=re.IGNORECASE):
            continue
        cleaned_lines.append(stripped)

    text = " ".join(cleaned_lines)
    text = re.sub(r"\s+", " ", text).strip()          # collapse whitespace
    text = re.sub(r"-\s+(?=[a-z])", "", text)          # rejoin hyphenated line-break words: "adapta- tion" -> "adaptation"
    return text


def preprocess_document(row: dict) -> dict:
    """
    Process a single document (one row from metadata.csv).
    Returns a log entry dict; also writes the cleaned JSON to data/processed/.
    """
    pdf_path = RAW_DIR / row["filename"]
    log_entry = {
        "filename": row["filename"],
        "title": row["title"],
        "source": row["source"],
        "status": "ok",
        "num_pages": 0,
        "total_chars": 0,
        "warning": "",
    }

    if not pdf_path.exists():
        log_entry["status"] = "error"
        log_entry["warning"] = "file not found in data/raw/"
        return log_entry

    try:
        raw_pages = _extract_pages(pdf_path)
    except Exception as e:  # corrupt/unreadable PDF
        log_entry["status"] = "error"
        log_entry["warning"] = f"extraction failed: {e}"
        return log_entry

    repeated_lines = _find_repeated_lines(raw_pages)
    cleaned_pages = [_clean_page_text(p, repeated_lines) for p in raw_pages]

    total_chars = sum(len(p) for p in cleaned_pages)
    log_entry["num_pages"] = len(cleaned_pages)
    log_entry["total_chars"] = total_chars

    if total_chars < MIN_TEXT_LENGTH:
        log_entry["status"] = "low_text"
        log_entry["warning"] = "very little extractable text — likely a scanned/image PDF, needs OCR"

    output = {
        "filename": row["filename"],
        "title": row["title"],
        "source": row["source"],
        "topic": row["topic"],
        "num_pages": len(cleaned_pages),
        "pages": [
            {"page_number": i + 1, "text": text}
            for i, text in enumerate(cleaned_pages)
        ],
    }

    out_path = PROCESSED_DIR / f"{pdf_path.stem}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return log_entry


def run_preprocessing() -> None:
    rows = _load_metadata()
    if not rows:
        print("metadata.csv is empty — nothing to preprocess.")
        return

    log_entries = []
    print(f"Preprocessing {len(rows)} document(s)...")
    for row in rows:
        entry = preprocess_document(row)
        status_marker = {"ok": "[ok]  ", "low_text": "[warn]", "error": "[fail]"}[entry["status"]]
        print(f"  {status_marker} {entry['filename']}  "
              f"({entry['num_pages']} pages, {entry['total_chars']} chars) {entry['warning']}")
        log_entries.append(entry)

    with open(PREPROCESS_LOG, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(log_entries[0].keys()))
        writer.writeheader()
        writer.writerows(log_entries)

    ok = sum(1 for e in log_entries if e["status"] == "ok")
    low = sum(1 for e in log_entries if e["status"] == "low_text")
    err = sum(1 for e in log_entries if e["status"] == "error")
    print(f"\nDone. {ok} ok, {low} low-text (may need OCR), {err} failed.")
    print(f"Cleaned text saved to: {PROCESSED_DIR}")
    print(f"Full log saved to:     {PREPROCESS_LOG}")


if __name__ == "__main__":
    run_preprocessing()
