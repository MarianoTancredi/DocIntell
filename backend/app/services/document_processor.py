import os
import mimetypes
from pathlib import Path
from typing import BinaryIO
import PyPDF2
from PIL import Image
import pytesseract
import structlog
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import settings

logger = structlog.get_logger()


class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def process_file(self, file: BinaryIO, filename: str) -> dict[str, any]:
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        try:
            if file_extension == ".pdf":
                content = await self._extract_pdf_text(file)
            elif file_extension == ".txt":
                content = await self._extract_text_content(file)
            elif file_extension in [".jpg", ".jpeg", ".png", ".tiff"]:
                content = await self._extract_image_text(file)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            chunks = self._split_text(content)
            
            return {
                "content": content,
                "chunks": chunks,
                "metadata": {
                    "filename": filename,
                    "file_type": file_extension,
                    "chunk_count": len(chunks),
                    "character_count": len(content)
                }
            }
        
        except Exception as e:
            logger.error("Document processing failed", filename=filename, error=str(e))
            raise
    
    async def _extract_pdf_text(self, file: BinaryIO) -> str:
        content = []
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    content.append(text)
            return "\n\n".join(content)
        except Exception as e:
            logger.error("PDF text extraction failed", error=str(e))
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    async def _extract_text_content(self, file: BinaryIO) -> str:
        try:
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return content
        except UnicodeDecodeError:
            logger.error("Text file encoding error")
            raise ValueError("Unable to decode text file. Please ensure it's UTF-8 encoded.")
    
    async def _extract_image_text(self, file: BinaryIO) -> str:
        try:
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error("OCR processing failed", error=str(e))
            raise ValueError(f"Failed to extract text from image: {str(e)}")
    
    def _split_text(self, content: str) -> list[str]:
        if not content or not content.strip():
            return []
        
        chunks = self.text_splitter.split_text(content)
        return [chunk.strip() for chunk in chunks if chunk.strip()]