# DocIntell API Documentation

## Authentication

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "full_name": "Full Name" // optional
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=username&password=password
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Documents

### Upload Document
```http
POST /api/v1/documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary data>
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "file_type": "application/pdf",
  "file_size": 1024000,
  "content": "Document content...",
  "metadata": {
    "filename": "document.pdf",
    "chunk_count": 5,
    "character_count": 2500
  },
  "processing_status": "completed",
  "created_at": "2023-01-01T00:00:00Z",
  "chunks": [...]
}
```

### List Documents
```http
GET /api/v1/documents/
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "document.pdf",
    "file_type": "application/pdf",
    "file_size": 1024000,
    "processing_status": "completed",
    "created_at": "2023-01-01T00:00:00Z",
    "metadata": {...}
  }
]
```

### Get Document
```http
GET /api/v1/documents/{document_id}
Authorization: Bearer <token>
```

### Delete Document
```http
DELETE /api/v1/documents/{document_id}
Authorization: Bearer <token>
```

## Chat

### Send Message
```http
POST /api/v1/chat/
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "What is this document about?",
  "conversation_id": "uuid" // optional for new conversation
}
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "This document discusses...",
  "sources": [
    {
      "content": "Relevant document chunk...",
      "metadata": {
        "filename": "document.pdf",
        "chunk_index": 2
      },
      "similarity": 0.85
    }
  ]
}
```

### List Conversations
```http
GET /api/v1/chat/conversations
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Document Analysis",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T01:00:00Z",
    "messages": []
  }
]
```

### Get Conversation
```http
GET /api/v1/chat/conversations/{conversation_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Document Analysis",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T01:00:00Z",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "role": "user",
      "content": "What is this document about?",
      "created_at": "2023-01-01T00:00:00Z",
      "metadata": {}
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "This document discusses...",
      "created_at": "2023-01-01T00:01:00Z",
      "metadata": {}
    }
  ]
}
```

## Users

### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

### Update Current User
```http
PUT /api/v1/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com", // optional
  "username": "newusername", // optional
  "full_name": "New Full Name", // optional
  "password": "newpassword" // optional
}
```

## Health & Monitoring

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Metrics
```http
GET /metrics
```

Returns Prometheus-formatted metrics.

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error description"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- Document upload: 10 requests per hour
- Chat endpoints: 60 requests per minute
- Other endpoints: 100 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in window
- `X-RateLimit-Reset`: Window reset time

## Supported File Types

The document upload endpoint supports:
- PDF (`.pdf`)
- Text files (`.txt`)
- Microsoft Word (`.doc`, `.docx`)
- Images with OCR (`.jpg`, `.jpeg`, `.png`, `.tiff`)

Maximum file size: 10MB