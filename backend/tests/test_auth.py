import pytest
from httpx import AsyncClient


class TestAuth:
    async def test_register_user(self, client: AsyncClient):
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword",
            "full_name": "New User"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
    
    async def test_register_duplicate_user(self, client: AsyncClient, test_user):
        user_data = {
            "email": test_user.email,
            "username": test_user.username,
            "password": "password",
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    async def test_login_valid_credentials(self, client: AsyncClient, test_user):
        login_data = {
            "username": test_user.username,
            "password": "testpassword",
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client: AsyncClient, test_user):
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword",
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        login_data = {
            "username": "nonexistent",
            "password": "password",
        }
        
        response = await client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401