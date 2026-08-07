"""
main.py
Entry point for the Climate CoPilot pipeline — currently covers
Weeks 1-3 (Data Collection -> Preprocessing). Chunking, embeddings,
FAISS, and the RAG pipeline plug in as later stages using the same
pattern.

Usage:
    python main.py collect --folder ~/Downloads/fao_pdfs --source FAO --topic "crop adaptation"
    python main.py preprocess
    python main.py summary
"""

import argparse

import data_collection
import preprocessing


def main():
    parser = argparse.ArgumentParser(description="Climate CoPilot data pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Register local PDFs into the pipeline")
    collect_parser.add_argument("--folder", required=True, help="Folder containing PDFs to import")
    collect_parser.add_argument("--source", required=True, help="e.g. FAO, IPCC, ICAR, IMD, MoEFCC")
    collect_parser.add_argument("--topic", required=True, help="e.g. 'crop adaptation', 'water management'")

    subparsers.add_parser("preprocess", help="Extract & clean text from every collected PDF")
    subparsers.add_parser("summary", help="Show how many documents have been collected")

    args = parser.parse_args()

    if args.command == "collect":
        data_collection.register_local_pdfs(args.folder, source=args.source, topic=args.topic)
    elif args.command == "preprocess":
        preprocessing.run_preprocessing()
    elif args.command == "summary":
        data_collection.collection_summary()


if __name__ == "__main__":
    main()
