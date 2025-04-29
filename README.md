# Engineering Paper Summarizer

A Python library for generating application-focused, hierarchical summaries of research papers, structured for engineers with practical takeaways and implementation insights.

## Features

- 📄 **PDF Text Extraction**: Automatically extracts full text from research papers
- 🔍 **Smart Section Detection**: Identifies and processes key paper sections
- 🧠 **Hierarchical Summarization**: Map-reduce approach for detailed yet concise summaries
- 💡 **Engineer's Focus**: Emphasizes practical applications and implementation insights
- 🔑 **Key Takeaways**: Highlights the most important insights and innovations
- ⚙️ **Engineer's Corner**: Dedicated section with practical implementation advice
- 📚 **Batch Processing**: Process multiple papers at once

## Installation

### From PyPI
```bash
pip install engpapersumm
```

### From Source
```bash
git clone https://github.com/MMWilliams/engineering-paper-summarizer.git
cd engineering-paper-summarizer
pip install -e .
```

## Quick Start

### Basic Usage
```python
from pathlib import Path
from engpapersumm import PaperSummarizer

# Initialize summarizer
summarizer = PaperSummarizer()

# Summarize a single paper
output_file = summarizer.summarize_file(
    pdf_path=Path("path/to/paper.pdf"),
    output_dir=Path("./output")
)

# Or process all PDFs in a directory
output_files = summarizer.summarize_directory(
    dir_path=Path("./papers"),
    output_dir=Path("./summaries")
)
```

### Command Line Usage
```bash
# Summarize a single paper
engpapersumm --pdf path/to/paper.pdf --out-dir ./summaries

# Process all papers in a directory
engpapersumm --input-dir ./papers --out-dir ./summaries

# Use a specific OpenAI model
engpapersumm --pdf path/to/paper.pdf --model gpt-4
```

## Configuration

You can customize the summarizer by passing a configuration dictionary:

```python
config = {
    "CHUNK_SIZE": 15000,  # Maximum characters per LLM call
    "MIN_SIMILARITY": 0.15,  # Minimum topic similarity threshold
    "LLM_MODEL": "gpt-4o"  # OpenAI model to use
}

summarizer = PaperSummarizer(config)
```

## Requirements

- Python 3.8+
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)
- Required Python packages (automatically installed):
  - PyPDF2
  - scikit-learn
  - openai
  - reportlab
  - python-dotenv

## Output

The library generates a formatted PDF report for each paper with:

1. **Key Takeaways**: Highlighting the most important insights
2. **Research Summary**: A detailed, hierarchical summary organized by paper sections
3. **Engineer's Corner**: Practical implementation advice and code examples

## Developer Guide

### Development Mode
```bash
# Install in development mode
pip install -e .
```

### Building a Distribution
```bash
# Install build tools
python -m pip install --upgrade build
# Create distribution packages
python -m build
```

### Publishing to PyPI
```bash
# Install twine
python -m pip install --upgrade twine
# Upload to PyPI
python -m twine upload dist/*
```

## License

MIT