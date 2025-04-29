"""Utilities for extracting and processing sections from research papers."""

import re
from typing import List, Dict

def extract_abstract(text: str) -> str:
    """
    Attempt to extract abstract from paper text.
    Returns abstract text or an empty string if not found.
    """
    # Try several common abstract patterns
    abstract_patterns = [
        r'(?i)abstract\s*\n+(.*?)(?:\n\s*\n|\n(?:[A-Z]|\d))',  # Most common format
        r'(?i)abstract[:\.\s]+(.*?)(?:\n\s*\n|\n(?:[A-Z]|\d))',  # Abstract with punctuation
        r'(?i)ABSTRACT\s*(.*?)(?:\n\s*\n|\n(?:[A-Z]|\d))',  # All caps
        r'(?i)abstract(?:\s*|:\s*)(.*?)(?=\n\s*\n\s*(?:introduction|1\.)\s*\n)',  # Until introduction
    ]
    
    for pattern in abstract_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            abstract = match.group(1).strip()
            # Clean up the abstract text
            abstract = re.sub(r'\s+', ' ', abstract)
            if len(abstract) > 50:  # Ensure we have a substantial abstract
                return abstract
    
    # If no abstract found, extract the first paragraph as a fallback
    first_para = text.split('\n\n')[0]
    if len(first_para) > 100:
        return first_para[:500]  # Limit to 500 chars
    return ""

def detect_sections(text: str, section_patterns: List[str], max_chars: int) -> List[dict]:
    """
    Identify academic paper sections using regex pattern matching.
    Returns a list of dictionaries with section title and content.
    """
    # First, try to find section headers with more specific patterns
    sections = []
    
    # More specific pattern for section headers
    combined_pattern = r'(?:^|\n\s*\n)(' + \
                      r'\d+\.\s*(?:' + '|'.join(section_patterns) + r')|' + \
                      r'(?:' + '|'.join(section_patterns) + r'))(?:\s*\n)'
    
    # Use case-insensitive search
    section_matches = list(re.finditer(combined_pattern, text, re.IGNORECASE))
    
    # Filter out matches that appear too close to one another (likely false positives)
    filtered_matches = []
    last_end = 0
    min_section_size = 1000  # Minimum characters between sections
    
    for match in section_matches:
        if match.start() - last_end > min_section_size or last_end == 0:
            filtered_matches.append(match)
            last_end = match.end()
    
    # If we found at least 2 genuine sections
    if len(filtered_matches) >= 2:
        for i, match in enumerate(filtered_matches):
            start_pos = match.start()
            
            # Extract the section title - use group 1 or the whole match
            section_title = match.group(1) if match.group(1) else match.group(0)
            # Clean up section title
            section_title = re.sub(r'^\d+\.\s*', '', section_title)  # Remove numbering
            section_title = section_title.strip().capitalize()
            
            # Determine end position (either next section or end of text)
            end_pos = filtered_matches[i+1].start() if i < len(filtered_matches)-1 else len(text)
            
            # Extract content without the section title
            content = text[match.end():end_pos].strip()
            
            if len(content) > 200:  # Only add if there's substantial content
                sections.append({
                    'title': section_title,
                    'content': content
                })
    
    # If no meaningful sections found or too few, use a simpler approach
    if len(sections) < 2:
        print("Using fallback section detection (basic structure)...")
        # Try to find abstract
        abstract_match = re.search(r'(?i)abstract(?:\s*\n)(.*?)(?:\n\s*\n|\n(?:[A-Z]|\d))', text, re.DOTALL)
        # Find introduction - one of the most reliable sections
        intro_match = re.search(r'(?i)(?:^|\n\s*\n)(?:\d\.\s*)?introduction(?:\s*\n)(.*?)(?:\n\s*\n\d|$)', text, re.DOTALL)
        
        text_len = len(text)
        # Determine positions to split the document into meaningful chunks
        if abstract_match and intro_match:
            # We found both abstract and introduction
            sections = [
                {'title': 'Abstract', 'content': abstract_match.group(1).strip()},
                {'title': 'Introduction', 'content': intro_match.group(1).strip()},
                {'title': 'Main Body', 'content': text[intro_match.end():int(text_len*0.8)]},
                {'title': 'Conclusion', 'content': text[int(text_len*0.8):]}
            ]
        elif intro_match:
            # Only introduction found
            sections = [
                {'title': 'Introduction', 'content': intro_match.group(1).strip()},
                {'title': 'Main Body', 'content': text[intro_match.end():int(text_len*0.8)]},
                {'title': 'Conclusion', 'content': text[int(text_len*0.8):]}
            ]
        else:
            # No clear sections found, split by proportion
            sections = [
                {'title': 'Introduction', 'content': text[:int(text_len*0.25)]},
                {'title': 'Methods and Results', 'content': text[int(text_len*0.25):int(text_len*0.75)]},
                {'title': 'Discussion and Conclusion', 'content': text[int(text_len*0.75):]}
            ]
    
    # Process detected sections to ensure they're not too large
    from ..utils.text import chunk_text
    
    processed_sections = []
    for section in sections:
        # If section is too large, split it further
        if len(section['content']) > max_chars:
            subsections = chunk_text(section['content'], max_chars)
            for i, subsection in enumerate(subsections):
                processed_sections.append({
                    'title': f"{section['title']} (Part {i+1})",
                    'content': subsection
                })
        else:
            processed_sections.append(section)
    
    print(f"Detected {len(processed_sections)} sections after processing")
    return processed_sections