from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any


class DocumentChunkResponse(BaseModel):
    id: UUID
    chunk_index: int
    content: str
    tokens: int | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int


class DocumentResponse(DocumentBase):
    id: UUID
    content: str | None
    metadata: Dict[str, Any]
    processing_status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime | None
    processed_at: datetime | None
    chunks: List[DocumentChunkResponse] = []
    
    class Config:
        from_attributes = True


class DocumentListResponse(DocumentBase):
    id: UUID
    processing_status: str
    created_at: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True