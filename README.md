# Climate CoPilot — Data Collection & Preprocessing (Weeks 1–3)

This is the first stage of the pipeline: collecting source PDFs and
turning them into clean, page-level text ready for chunking.

## Setup

```bash
pip install -r requirements.txt
```

## 1. Collect documents

Download PDFs manually from FAO / IPCC / ICAR / IMD / MoEFCC (most require
a browser, so this is a manual step), put them in one folder, then:

```bash
python main.py collect --folder /path/to/your/pdfs --source FAO --topic "crop adaptation"
```

Run this once per source/topic batch. It copies files into `data/raw/`
and logs each one (title, source, topic, hash) in `data/raw/metadata.csv`.
Re-running on the same files is safe — duplicates are skipped by content hash.

Check progress any time:

```bash
python main.py summary
```

## 2. Preprocess (extract + clean text)

```bash
python main.py preprocess
```

For every document in `metadata.csv`, this:
- extracts text page-by-page with PyMuPDF
- detects and strips repeated headers/footers/page numbers
- collapses whitespace and rejoins hyphenated line breaks
- saves cleaned, page-level text to `data/processed/<name>.json`
- logs per-document stats to `logs/preprocessing_log.csv`

Documents with very little extractable text are flagged `low_text` in the
log — that usually means the PDF is scanned/image-based and will need OCR
before it's usable (not handled by this stage).

## Project structure

```
climate_copilot/
├── config.py            # paths & settings
├── data_collection.py   # Week 1-2: gather PDFs + metadata.csv
├── preprocessing.py     # Week 3: extract & clean text -> JSON
├── main.py               # CLI entry point
├── requirements.txt
└── data/
    ├── raw/              # original PDFs + metadata.csv
    └── processed/        # cleaned per-document JSON (page-level text)
```

## Next stage (not yet built)

Week 4 (chunking) reads `data/processed/*.json` and splits each page's
text into smaller overlapping passages, ready for embedding.
