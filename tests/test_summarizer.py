"""Test the PaperSummarizer class."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import os
from engpapersumm import PaperSummarizer

# Sample configuration for testing
TEST_CONFIG = {
    "CHUNK_SIZE": 5000,
    "MIN_SIMILARITY": 0.1,
    "LLM_MODEL": "gpt-4o"
}

# Skip tests if OPENAI_API_KEY is not set
pytestmark = pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") is None,
    reason="OPENAI_API_KEY environment variable not set"
)

class TestPaperSummarizer:
    """Tests for the PaperSummarizer class."""
    
    def test_init(self):
        """Test initializing the summarizer."""
        summarizer = PaperSummarizer(config=TEST_CONFIG)
        assert summarizer.config["CHUNK_SIZE"] == 5000
        assert summarizer.config["MIN_SIMILARITY"] == 0.1
        assert summarizer.config["LLM_MODEL"] == "gpt-4o"
    
    @patch("engpapersumm.summarizer.extract_text_and_title")
    @patch("engpapersumm.summarizer.generate_key_takeaways")
    @patch("engpapersumm.summarizer.generate_engineers_corner")
    @patch("engpapersumm.summarizer.write_summary_pdf")
    def test_summarize_file(self, mock_write_pdf, mock_engineers_corner, 
                          mock_takeaways, mock_extract):
        """Test summarizing a file."""
        # Set up mocks
        mock_extract.return_value = ("Sample text", "Sample Title")
        mock_takeaways.return_value = "Key takeaways"
        mock_engineers_corner.return_value = "Engineers corner"
        
        # Create summarizer with mocked _hierarchical_summarize
        summarizer = PaperSummarizer(config=TEST_CONFIG)
        summarizer._hierarchical_summarize = MagicMock(return_value="Summary")
        
        # Test
        pdf_path = Path("test.pdf")
        output_dir = Path("./output")
        result = summarizer.summarize_file(pdf_path, output_dir)
        
        # Assertions
        mock_extract.assert_called_once_with(pdf_path)
        summarizer._hierarchical_summarize.assert_called_once()
        mock_takeaways.assert_called_once()
        mock_engineers_corner.assert_called_once()
        mock_write_pdf.assert_called_once()
        assert result == output_dir / "Sample_Title-engineering-summary.pdf"
    
    @patch("engpapersumm.summarizer.list_pdfs")
    def test_summarize_directory(self, mock_list_pdfs):
        """Test summarizing a directory of files."""
        # Set up mock
        mock_list_pdfs.return_value = [Path("test1.pdf"), Path("test2.pdf")]
        
        # Create summarizer with mocked summarize_file
        summarizer = PaperSummarizer(config=TEST_CONFIG)
        summarizer.summarize_file = MagicMock(
            side_effect=[Path("out1.pdf"), Path("out2.pdf")]
        )
        
        # Test
        input_dir = Path("./papers")
        output_dir = Path("./output")
        results = summarizer.summarize_directory(input_dir, output_dir)
        
        # Assertions
        mock_list_pdfs.assert_called_once_with(input_dir)
        assert summarizer.summarize_file.call_count == 2
        assert len(results) == 2
        assert results == [Path("out1.pdf"), Path("out2.pdf")]
    
    def test_empty_directory(self):
        """Test summarizing an empty directory."""
        with patch("engpapersumm.summarizer.list_pdfs", return_value=[]):
            summarizer = PaperSummarizer(config=TEST_CONFIG)
            results = summarizer.summarize_directory(Path("./empty"))
            assert results == []