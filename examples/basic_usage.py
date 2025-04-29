#!/usr/bin/env python3
"""
Basic usage example for the Engineering Paper Summarizer library.
"""

from pathlib import Path
from engpapersumm import PaperSummarizer

def main():
    # Initialize the summarizer with default configuration
    summarizer = PaperSummarizer()
    
    # Specify the path to a PDF file
    pdf_path = Path("path/to/your/paper.pdf")
    
    # Specify the output directory (optional, defaults to same directory as PDF)
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    # Summarize the paper
    output_file = summarizer.summarize_file(pdf_path, output_dir)
    
    print(f"Summary saved to: {output_file}")

if __name__ == "__main__":
    main()