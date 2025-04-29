"""Test PDF and section extraction functionality."""

import pytest
from pathlib import Path
import tempfile
import PyPDF2
from unittest.mock import patch, mock_open
from engpapersumm.extractors import pdf, section

class TestPdfExtractor:
    """Tests for PDF extraction utilities."""
    
    def test_list_pdfs_directory(self):
        """Test listing PDFs in a directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create some test files
            Path(f"{tmp_dir}/test1.pdf").touch()
            Path(f"{tmp_dir}/test2.pdf").touch()
            Path(f"{tmp_dir}/not_pdf.txt").touch()
            
            # Test the function
            pdfs = pdf.list_pdfs(Path(tmp_dir))
            
            # Assert we get the right files
            assert len(pdfs) == 2
            assert any(p.name == "test1.pdf" for p in pdfs)
            assert any(p.name == "test2.pdf" for p in pdfs)
            assert not any(p.name == "not_pdf.txt" for p in pdfs)
    
    def test_list_pdfs_single_file(self):
        """Test listing PDFs when given a single file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a test file
            test_file = Path(f"{tmp_dir}/test.pdf")
            test_file.touch()
            
            # Test the function
            pdfs = pdf.list_pdfs(test_file)
            
            # Assert we get the right file
            assert len(pdfs) == 1
            assert pdfs[0].name == "test.pdf"
    
    def test_list_pdfs_non_pdf(self):
        """Test listing PDFs when given a non-PDF file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create a test file
            test_file = Path(f"{tmp_dir}/test.txt")
            test_file.touch()
            
            # Test the function
            pdfs = pdf.list_pdfs(test_file)
            
            # Assert we get an empty list
            assert len(pdfs) == 0