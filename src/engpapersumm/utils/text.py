"""Text processing utilities for the Engineering Paper Summarizer."""

import re
from typing import List

def sanitize_filename(name: str) -> str:
    """Replace filesystem-invalid characters with underscore."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def chunk_text(text: str, max_chars: int) -> List[str]:
    """Break text into chunks of maximum size."""
    paras = text.split("\n\n")
    chunks, current = [], ""
    for p in paras:
        if len(current) + len(p) > max_chars:
            chunks.append(current)
            current = ""
        current += p + "\n\n"
    if current:
        chunks.append(current)
    return chunks