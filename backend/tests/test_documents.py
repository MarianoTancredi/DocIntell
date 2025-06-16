import pytest
import io
from httpx import AsyncClient
from unittest.mock import patch, Mock


class TestDocuments:
    async def test_upload_document_success(self, authenticated_client: AsyncClient):
        file_content = b"This is a test document content."
        files = {
            "file": ("test.txt", io.BytesIO(file_content), "text/plain")
        }
        
        with patch("app.services.document_processor.DocumentProcessor.process_file") as mock_process, \
             patch("app.services.embedding_service.EmbeddingService.store_document_embeddings") as mock_store:
            
            mock_process.return_value = {
                "content": "This is a test document content.",
                "chunks": ["This is a test", "document content."],
                "metadata": {"filename": "test.txt", "chunk_count": 2}
            }
            mock_store.return_value = ["chunk1", "chunk2"]
            
            response = await authenticated_client.post(
                "/api/v1/documents/upload",
                files=files
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["processing_status"] == "completed"
        assert "id" in data
    
    async def test_upload_document_processing_failure(self, authenticated_client: AsyncClient):
        file_content = b"This is a test document content."
        files = {
            "file": ("test.txt", io.BytesIO(file_content), "text/plain")
        }
        
        with patch("app.services.document_processor.DocumentProcessor.process_file") as mock_process:
            mock_process.side_effect = Exception("Processing failed")
            
            response = await authenticated_client.post(
                "/api/v1/documents/upload",
                files=files
            )
        
        assert response.status_code == 500
        assert "Processing failed" in response.json()["detail"]
    
    async def test_list_documents(self, authenticated_client: AsyncClient):
        response = await authenticated_client.get("/api/v1/documents/")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    async def test_get_document_not_found(self, authenticated_client: AsyncClient):
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await authenticated_client.get(f"/api/v1/documents/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_delete_document_not_found(self, authenticated_client: AsyncClient):
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await authenticated_client.delete(f"/api/v1/documents/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]