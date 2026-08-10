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
import chunking
import indexing
import retrieval


def main():
    parser = argparse.ArgumentParser(description="Climate CoPilot data & retrieval pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Collection
    collect_parser = subparsers.add_parser("collect", help="Register local PDFs into the pipeline")
    collect_parser.add_argument("--folder", required=True, help="Folder containing PDFs to import")
    collect_parser.add_argument("--source", required=True, help="e.g. FAO, IPCC, ICAR, IMD, MoEFCC")
    collect_parser.add_argument("--topic", required=True, help="e.g. 'crop adaptation', 'water management'")

    # Preprocessing
    subparsers.add_parser("preprocess", help="Extract & clean text from every collected PDF")
    
    # Summary
    subparsers.add_parser("summary", help="Show how many documents have been collected")

    # Phase 2: Chunking
    subparsers.add_parser("chunk", help="Split preprocessed documents into overlapping passage chunks")

    # Phase 2: Indexing
    subparsers.add_parser("index", help="Generate embeddings and build FAISS vector index")

    # Phase 2: Search / Retrieval
    search_parser = subparsers.add_parser("search", help="Search FAISS vector index for relevant passages")
    search_parser.add_argument("--query", "-q", required=True, help="Search query string")
    search_parser.add_argument("--top_k", "-k", type=int, default=5, help="Number of top passages to retrieve (default: 5)")
    search_parser.add_argument("--source", help="Optional source filter (e.g. FAO, IPCC)")

    args = parser.parse_args()

    if args.command == "collect":
        data_collection.register_local_pdfs(args.folder, source=args.source, topic=args.topic)
    elif args.command == "preprocess":
        preprocessing.run_preprocessing()
    elif args.command == "summary":
        data_collection.collection_summary()
    elif args.command == "chunk":
        chunking.create_chunks()
    elif args.command == "index":
        indexing.build_index()
    elif args.command == "search":
        results = retrieval.search(args.query, top_k=args.top_k, source_filter=args.source)
        retrieval.print_search_results(args.query, results)


if __name__ == "__main__":
    main()
