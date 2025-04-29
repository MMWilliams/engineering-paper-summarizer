"""
Main summarizer class that orchestrates the paper processing pipeline.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from openai import OpenAI

from .extractors.pdf import extract_text_and_title, list_pdfs
from .extractors.section import detect_sections, extract_abstract
from .processors.topic import extract_paper_topic, compute_topic_similarity, filter_irrelevant_sections
from .processors.coherence import ensure_content_coherence
from .processors.validation import validate_content_against_title, perform_topic_modeling
from .generators.summary import map_summarize_section, reduce_summarize
from .generators.takeaways import generate_key_takeaways
from .generators.engineers_corner import generate_engineers_corner
from .formatters.pdf import write_summary_pdf
from .utils.text import sanitize_filename, chunk_text

# Load environment variables from .env file
load_dotenv()

# Default configuration
DEFAULT_CONFIG = {
    "CHUNK_SIZE": 15_000,  # chars per LLM call
    "SECTION_TITLES": [
        r"abstract",
        r"introduction",
        r"related work",
        r"background",
        r"methodology|methods|method",
        r"experiment(s|al setup)?",
        r"implementation|architecture",
        r"results",
        r"discussion",
        r"(future work|limitations)",
        r"conclusion(s)?",
        r"reference(s)?|bibliography"
    ],
    "MIN_SIMILARITY": 0.15,  # Minimum similarity threshold for topic filtering
    "LLM_MODEL": "gpt-4o"
}

class PaperSummarizer:
    """
    Main class for summarizing research papers into engineer-focused summaries.
    """
    
    def __init__(self, config=None):
        """
        Initialize the summarizer with configuration settings.
        
        Args:
            config (dict, optional): Configuration parameters to override defaults.
        """
        # Set up configuration
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
    
    def summarize_file(self, pdf_path: Path, output_dir: Path = None) -> Path:
        """
        Summarize a single PDF file and save the result.
        
        Args:
            pdf_path (Path): Path to the PDF file
            output_dir (Path, optional): Directory to save the output. Defaults to same as input.
            
        Returns:
            Path: Path to the generated summary file
        """
        if not output_dir:
            output_dir = pdf_path.parent
        
        # Extract text from the PDF
        text, title = extract_text_and_title(pdf_path)
        
        # Perform hierarchical summarization
        print(f"⏳ Processing {pdf_path.name}...")
        summary = self._hierarchical_summarize(text, title)
        
        # Generate key takeaways
        print("Generating key takeaways...")
        key_takeaways = generate_key_takeaways(self.client, text, title, self.config["LLM_MODEL"])
        
        # Generate Engineer's Corner section
        print("Generating Engineer's Corner...")
        engineers_corner = generate_engineers_corner(self.client, text, title, self.config["LLM_MODEL"])
        
        # Write to PDF
        safe_title = sanitize_filename(title)
        out_file = output_dir / f"{safe_title}-engineering-summary.pdf"
        write_summary_pdf(out_file, title, summary, key_takeaways, engineers_corner)
        print(f"✅ Saved: {out_file}")
        
        return out_file
    
    def summarize_directory(self, dir_path: Path, output_dir: Path = None) -> List[Path]:
        """
        Summarize all PDFs in a directory.
        
        Args:
            dir_path (Path): Directory containing PDF files
            output_dir (Path, optional): Directory to save outputs. Defaults to input directory.
            
        Returns:
            List[Path]: Paths to all generated summary files
        """
        if not output_dir:
            output_dir = dir_path
            
        pdf_files = list_pdfs(dir_path)
        if not pdf_files:
            print("⚠️  No PDF files found. Exiting.")
            return []
        
        output_files = []
        for pdf_path in pdf_files:
            out_file = self.summarize_file(pdf_path, output_dir)
            output_files.append(out_file)
            
        return output_files

    def _hierarchical_summarize(self, text: str, title: str) -> str:
        """
        Perform hierarchical (Map-Reduce) summarization on the paper text.
        First detects sections, applies content coherence checks, then summarizes each section,
        and finally combines them into a coherent summary.
        """
        # Extract abstract for topic analysis
        abstract = extract_abstract(text)
        print(f"Extracted abstract: {abstract[:200]}...")
        
        # 1. Extract main topics from title and abstract
        print("Extracting main paper topics...")
        topic_dict = extract_paper_topic(self.client, title, abstract, self.config["LLM_MODEL"])
        print(f"Extracted topics: {topic_dict}")
        
        # 2. Detect sections in the paper
        sections = detect_sections(text, self.config["SECTION_TITLES"], self.config["CHUNK_SIZE"])
        print(f"Initially detected {len(sections)} sections")
        
        # 3. Filter sections by topic relevance
        print("Filtering sections by topic relevance...")
        relevant_sections = filter_irrelevant_sections(sections, topic_dict, self.config["MIN_SIMILARITY"])
        print(f"After topic filtering: {len(relevant_sections)} sections")
        
        # 4. Ensure coherence between sections
        print("Ensuring content coherence between sections...")
        coherent_sections = ensure_content_coherence(relevant_sections)
        print(f"After coherence check: {len(coherent_sections)} sections")
        
        # 5. Validate sections against paper title
        print("Validating sections against paper title...")
        validated_sections = validate_content_against_title(self.client, title, coherent_sections, self.config["LLM_MODEL"])
        print(f"After title validation: {len(validated_sections)} sections")
        
        # 6. Perform topic modeling on final sections
        print("Performing topic modeling on final sections...")
        topics = perform_topic_modeling(self.client, validated_sections, self.config["LLM_MODEL"])
        print(f"Identified topics: {topics}")
        
        # 7. Map phase: Summarize each validated section
        print(f"Map phase: Summarizing {len(validated_sections)} sections...")
        section_summaries = []
        for i, section in enumerate(validated_sections):
            print(f"  Processing section {i+1}/{len(validated_sections)}: {section['title']}")
            
            # Create topic guidance for more focused summarization
            if topics:
                topic_terms = ", ".join([", ".join(topic_list) for topic_list in topics])
                section['topic_guidance'] = f"Focus on these key topics: {topic_terms}"
            else:
                section['topic_guidance'] = ""
                
            summary = map_summarize_section(self.client, section, self.config["LLM_MODEL"])
            section_summaries.append(summary)
        
        # 8. Reduce phase: Fuse section summaries into a coherent whole
        print("Reduce phase: Synthesizing section summaries...")
        final_summary = reduce_summarize(self.client, section_summaries, self.config["LLM_MODEL"])
        
        return final_summary