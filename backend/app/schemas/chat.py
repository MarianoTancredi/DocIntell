from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any, Optional


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None


class ChatSource(BaseModel):
    content: str
    metadata: Dict[str, Any]
    similarity: float


class ChatResponse(BaseModel):
    conversation_id: UUID
    message: str
    sources: List[ChatSource]


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime | None
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True