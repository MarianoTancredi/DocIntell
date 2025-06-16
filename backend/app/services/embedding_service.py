import uuid
from typing import List
import openai
import structlog
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=settings.EMBEDDING_MODEL
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            raise
    
    async def store_document_embeddings(
        self, 
        document_id: str, 
        chunks: List[str], 
        metadata: dict = None
    ) -> List[str]:
        try:
            embeddings = await self.generate_embeddings(chunks)
            
            chunk_ids = [f"{document_id}_{i}" for i in range(len(chunks))]
            
            metadatas = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "document_id": document_id,
                    "chunk_index": i,
                    "text_length": len(chunk),
                    **(metadata or {})
                }
                metadatas.append(chunk_metadata)
            
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            logger.info(
                "Document embeddings stored", 
                document_id=document_id, 
                chunk_count=len(chunks)
            )
            
            return chunk_ids
        
        except Exception as e:
            logger.error("Failed to store document embeddings", error=str(e))
            raise
    
    async def search_similar_documents(
        self, 
        query: str, 
        n_results: int = 5,
        document_filter: dict = None
    ) -> dict:
        try:
            query_embedding = await self.generate_embeddings([query])
            
            where_clause = document_filter if document_filter else None
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
        
        except Exception as e:
            logger.error("Document search failed", error=str(e))
            raise
    
    def delete_document_embeddings(self, document_id: str):
        try:
            self.collection.delete(
                where={"document_id": document_id}
            )
            logger.info("Document embeddings deleted", document_id=document_id)
        except Exception as e:
            logger.error("Failed to delete document embeddings", error=str(e))
            raise