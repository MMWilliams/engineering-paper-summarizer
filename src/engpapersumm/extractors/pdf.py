"""PDF extraction utilities for processing research papers."""

import re
from pathlib import Path
from typing import List, Tuple
import PyPDF2

def list_pdfs(path: Path) -> List[Path]:
    """Return all .pdf files under path (if directory) or [path] if file."""
    if path.is_dir():
        return list(path.glob("*.pdf"))
    if path.suffix.lower() == ".pdf":
        return [path]
    return []

def extract_text_and_title(pdf_path: Path) -> Tuple[str, str]:
    """Extract text and title from a PDF file."""
    reader = PyPDF2.PdfReader(str(pdf_path))
    meta = reader.metadata
    title = meta.title or pdf_path.stem
    text_chunks = []
    for page in reader.pages:
        raw = page.extract_text() or ""
        cleaned = re.sub(r"\s*\n\s*", " ", raw)  # collapse line breaks
        text_chunks.append(cleaned)
    return " ".join(text_chunks), title