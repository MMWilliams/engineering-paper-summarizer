#!/usr/bin/env python3
"""
Example showing how to process multiple PDFs in a directory.
"""

from pathlib import Path
from engpapersumm import PaperSummarizer

def main():
    # Initialize the summarizer with custom configuration
    custom_config = {
        "CHUNK_SIZE": 10000,  # Smaller chunks for processing
        "MIN_SIMILARITY": 0.2,  # Stricter section filtering
        "LLM_MODEL": "gpt-4o"  # Specify model to use
    }
    summarizer = PaperSummarizer(config=custom_config)
    
    # Specify the directory containing PDFs
    input_dir = Path("./papers")
    
    # Specify the output directory
    output_dir = Path("./summaries")
    output_dir.mkdir(exist_ok=True)
    
    # Process all PDFs in the directory
    output_files = summarizer.summarize_directory(input_dir, output_dir)
    
    # Print output information
    print(f"Processed {len(output_files)} papers:")
    for file in output_files:
        print(f"  - {file.name}")

if __name__ == "__main__":
    main()