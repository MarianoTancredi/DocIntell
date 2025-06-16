import pytest
from httpx import AsyncClient
from unittest.mock import patch, Mock


class TestChat:
    async def test_chat_new_conversation(self, authenticated_client: AsyncClient):
        chat_data = {
            "message": "What is this document about?",
            "conversation_id": None
        }
        
        mock_response = {
            "response": "This document is about testing.",
            "sources": [
                {
                    "content": "Test content",
                    "metadata": {"filename": "test.txt"},
                    "similarity": 0.85
                }
            ]
        }
        
        with patch("app.services.chat_service.ChatService.generate_response") as mock_chat:
            mock_chat.return_value = mock_response
            
            response = await authenticated_client.post(
                "/api/v1/chat/",
                json=chat_data
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["message"] == mock_response["response"]
        assert len(data["sources"]) == 1
    
    async def test_chat_existing_conversation(self, authenticated_client: AsyncClient):
        conversation_id = "550e8400-e29b-41d4-a716-446655440000"
        chat_data = {
            "message": "Tell me more",
            "conversation_id": conversation_id
        }
        
        mock_response = {
            "response": "Here's more information.",
            "sources": []
        }
        
        with patch("app.services.chat_service.ChatService.generate_response") as mock_chat:
            mock_chat.return_value = mock_response
            
            response = await authenticated_client.post(
                "/api/v1/chat/",
                json=chat_data
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["message"] == mock_response["response"]
    
    async def test_chat_service_error(self, authenticated_client: AsyncClient):
        chat_data = {
            "message": "What is this document about?",
            "conversation_id": None
        }
        
        with patch("app.services.chat_service.ChatService.generate_response") as mock_chat:
            mock_chat.side_effect = Exception("Chat service failed")
            
            response = await authenticated_client.post(
                "/api/v1/chat/",
                json=chat_data
            )
        
        assert response.status_code == 500
        assert "Chat processing failed" in response.json()["detail"]
    
    async def test_get_conversations(self, authenticated_client: AsyncClient):
        response = await authenticated_client.get("/api/v1/chat/conversations")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    async def test_get_conversation_not_found(self, authenticated_client: AsyncClient):
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await authenticated_client.get(f"/api/v1/chat/conversations/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_delete_conversation_not_found(self, authenticated_client: AsyncClient):
        fake_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await authenticated_client.delete(f"/api/v1/chat/conversations/{fake_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]