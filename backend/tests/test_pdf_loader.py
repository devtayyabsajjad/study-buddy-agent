import unittest
import io
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.loaders.pdf_loader import read_pdf_bytes, validate_pdf_integrity
from backend.utils.error_handler import PDFProcessingError
from backend.utils.file_validator import FileValidationError

class TestPDFLoader(unittest.TestCase):
    def test_empty_pdf_validation(self):
        """Test that empty/invalid files are rejected."""
        # Empty bytes
        with self.assertRaises(FileValidationError):
            read_pdf_bytes(b"", max_size_mb=1.0)
            
        # Invalid PDF header
        with self.assertRaises(PDFProcessingError):
            read_pdf_bytes(b"Not a PDF file", max_size_mb=1.0)

    def test_file_size_limit(self):
        """Test that file size limits are enforced."""
        # Create dummy large file (2MB)
        large_content = b"%PDF-1.4\n" + b"0" * (2 * 1024 * 1024)
        
        with self.assertRaises(FileValidationError):
            read_pdf_bytes(large_content, max_size_mb=1.0)

    # Note: We can't easily test valid PDF parsing without a real PDF file
    # unless we mock pypdf or create a valid minimal PDF.
    # For now, we test the validation logic which was a source of errors.

if __name__ == "__main__":
    unittest.main()
