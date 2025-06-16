import pytest
import io
from unittest.mock import patch, Mock
from app.services.document_processor import DocumentProcessor


class TestDocumentProcessor:
    def setup_method(self):
        self.processor = DocumentProcessor()
    
    async def test_process_text_file(self):
        file_content = b"This is a test document.\n\nIt has multiple paragraphs."
        file = io.BytesIO(file_content)
        
        result = await self.processor.process_file(file, "test.txt")
        
        assert result["content"] == "This is a test document.\n\nIt has multiple paragraphs."
        assert len(result["chunks"]) > 0
        assert result["metadata"]["filename"] == "test.txt"
        assert result["metadata"]["file_type"] == ".txt"
    
    async def test_process_unsupported_file_type(self):
        file = io.BytesIO(b"content")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            await self.processor.process_file(file, "test.xyz")
    
    @patch('PyPDF2.PdfReader')
    async def test_process_pdf_file(self, mock_pdf_reader):
        mock_page = Mock()
        mock_page.extract_text.return_value = "PDF content here"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        file = io.BytesIO(b"fake pdf content")
        
        result = await self.processor.process_file(file, "test.pdf")
        
        assert result["content"] == "PDF content here"
        assert result["metadata"]["file_type"] == ".pdf"
    
    async def test_split_text_empty_content(self):
        chunks = self.processor._split_text("")
        assert chunks == []
    
    async def test_split_text_short_content(self):
        content = "Short content"
        chunks = self.processor._split_text(content)
        assert len(chunks) == 1
        assert chunks[0] == content
    
    async def test_split_text_long_content(self):
        content = "A" * 2000  # Long content that should be split
        chunks = self.processor._split_text(content)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 1000  # Based on chunk_size in config