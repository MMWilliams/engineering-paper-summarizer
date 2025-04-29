#!/usr/bin/env python3
"""
Command-line interface for the Engineering Paper Summarizer library.
"""

import argparse
from pathlib import Path
from . import PaperSummarizer

def main():
    parser = argparse.ArgumentParser(
        description="Generate application-focused engineering summaries of research papers."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf", type=Path, help="Path to a single PDF")
    group.add_argument("--input-dir", type=Path, help="Directory containing PDFs")
    parser.add_argument("--out-dir", type=Path, default=Path("."), help="Output directory")
    parser.add_argument("--min-similarity", type=float, default=0.15, 
                       help="Minimum similarity threshold for topic filtering (0-1)")
    parser.add_argument("--model", type=str, default="gpt-4o",
                       help="OpenAI model to use for summarization")
    args = parser.parse_args()

    # Create configuration
    config = {
        "MIN_SIMILARITY": args.min_similarity,
        "LLM_MODEL": args.model
    }
    
    # Create summarizer
    summarizer = PaperSummarizer(config)
    
    if args.pdf:
        summarizer.summarize_file(args.pdf, args.out_dir)
    elif args.input_dir:
        summarizer.summarize_directory(args.input_dir, args.out_dir)

if __name__ == "__main__":
    main()