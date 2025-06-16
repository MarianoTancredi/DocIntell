from typing import List, Dict, Any
import openai
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.models.conversation import Conversation, Message
from app.models.user import User

logger = structlog.get_logger()


class ChatService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()
    
    async def generate_response(
        self,
        user_message: str,
        conversation_id: str,
        user_id: int,
        db: AsyncSession,
        max_context_chunks: int = 5
    ) -> Dict[str, Any]:
        try:
            relevant_docs = await self.embedding_service.search_similar_documents(
                query=user_message,
                n_results=max_context_chunks,
                document_filter={"owner_id": user_id}
            )
            
            context = "\n\n".join([
                f"Document: {doc}" 
                for doc in relevant_docs["documents"]
            ])
            
            conversation_history = await self._get_conversation_history(
                conversation_id, db
            )
            
            system_prompt = self._build_system_prompt(context)
            messages = self._build_messages(system_prompt, conversation_history, user_message)
            
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            await self._save_messages(
                conversation_id, user_message, assistant_message, db
            )
            
            return {
                "response": assistant_message,
                "sources": [
                    {
                        "content": doc,
                        "metadata": meta,
                        "similarity": 1 - distance
                    }
                    for doc, meta, distance in zip(
                        relevant_docs["documents"],
                        relevant_docs["metadatas"],
                        relevant_docs["distances"]
                    )
                ]
            }
        
        except Exception as e:
            logger.error("Chat response generation failed", error=str(e))
            raise
    
    def _build_system_prompt(self, context: str) -> str:
        return f"""You are an AI assistant that helps users understand and analyze their documents. 
        Use the following context from the user's documents to answer their questions accurately and helpfully.
        
        Context from documents:
        {context}
        
        Instructions:
        - Answer based primarily on the provided context
        - If the context doesn't contain enough information, clearly state this
        - Be concise but thorough in your responses
        - Cite specific parts of documents when relevant
        - If asked about something not in the context, politely explain the limitation"""
    
    def _build_messages(
        self, 
        system_prompt: str, 
        conversation_history: List[Dict[str, str]], 
        user_message: str
    ) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def _get_conversation_history(
        self, 
        conversation_id: str, 
        db: AsyncSession
    ) -> List[Dict[str, str]]:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(20)
        )
        messages = result.scalars().all()
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    async def _save_messages(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        db: AsyncSession
    ):
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )
        
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message
        )
        
        db.add(user_msg)
        db.add(assistant_msg)
        await db.commit()