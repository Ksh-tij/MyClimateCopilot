"""
main.py
Entry point for the Climate CoPilot pipeline — covers data collection,
preprocessing, chunking, indexing, retrieval, RAG answer generation, and self-evaluation.

Usage:
    python main.py collect --folder ~/Downloads/fao_pdfs --source FAO --topic "crop adaptation"
    python main.py preprocess
    python main.py summary
    python main.py chunk
    python main.py index
    python main.py search -q "climate change impacts on agriculture"
    python main.py ask -q "How will climate change affect wheat yields?"
    python main.py ask -q "How will climate change affect wheat yields?" --eval
"""

import argparse

import data_collection
import preprocessing
import chunking
import indexing
import retrieval
import generation
import evaluation


def main():
    parser = argparse.ArgumentParser(description="Climate CoPilot data & retrieval pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Collection
    collect_parser = subparsers.add_parser("collect", help="Register local PDFs into the pipeline")
    collect_parser.add_argument("--folder", required=True, help="Folder containing PDFs to import")
    collect_parser.add_argument("--source", required=True, help="e.g. FAO, IPCC, ICAR, IMD, MoEFCC")
    collect_parser.add_argument("--topic", required=True, help="e.g. 'crop adaptation', 'water management'")

    # Preprocessing
    subparsers.add_parser("preprocess", help="Register and extract text from every PDF in data/raw")
    
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
    search_parser.add_argument(
        "--mode", "-m", choices=["dense", "bm25", "hybrid"], default="dense",
        help="Retrieval mode: dense (FAISS cosine similarity, default), bm25 (keyword search), "
             "or hybrid (both, merged via Reciprocal Rank Fusion)"
    )

    # Phase 3: Ask / RAG Answer Generation
    ask_parser = subparsers.add_parser("ask", help="Ask a climate question and get a grounded answer")
    ask_parser.add_argument("--query", "-q", required=True, help="Your climate adaptation question")
    ask_parser.add_argument("--top_k", "-k", type=int, default=5, help="Number of passages to retrieve (default: 5)")
    ask_parser.add_argument("--source", help="Optional source filter (e.g. FAO, IPCC)")
    ask_parser.add_argument(
        "--mode", "-m", choices=["dense", "bm25", "hybrid"], default="hybrid",
        help="Retrieval mode (default: hybrid)"
    )
    ask_parser.add_argument(
        "--model", default="llama-3.3-70b-versatile",
        help="Groq model to use (default: llama-3.3-70b-versatile)"
    )
    ask_parser.add_argument("--show-passages", action="store_true", help="Show retrieved passages in output")
    ask_parser.add_argument("--verbose", "-v", action="store_true", help="Show intermediate steps")
    ask_parser.add_argument("--eval", "-e", action="store_true", help="Run self-evaluation on the generated answer")

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
        results = retrieval.search(args.query, top_k=args.top_k, source_filter=args.source, mode=args.mode)
        retrieval.print_search_results(args.query, results, mode=args.mode)
    elif args.command == "ask":
        # Generate answer
        result = generation.generate_answer(
            question=args.query,
            top_k=args.top_k,
            source_filter=args.source,
            retrieval_mode=args.mode,
            model=args.model,
            verbose=args.verbose
        )
        generation.print_answer(result, show_passages=args.show_passages)
        
        # Run self-evaluation if requested
        if args.eval:
            eval_result = evaluation.evaluate_response(
                question=result["question"],
                answer=result["answer"],
                passages=result["passages"],
                verbose=args.verbose
            )
            evaluation.print_evaluation(eval_result)


if __name__ == "__main__":
    main()
