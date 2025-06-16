from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.api.deps import get_current_user
from app.schemas.document import DocumentResponse, DocumentListResponse

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    processor = DocumentProcessor()
    embedding_service = EmbeddingService()
    
    try:
        processed_data = await processor.process_file(file.file, file.filename)
        
        document = Document(
            filename=file.filename,
            file_type=file.content_type or "unknown",
            file_size=file.size or 0,
            content=processed_data["content"],
            metadata=processed_data["metadata"],
            owner_id=current_user.id,
            processing_status="processing"
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        chunk_ids = await embedding_service.store_document_embeddings(
            str(document.id),
            processed_data["chunks"],
            {"filename": file.filename, "owner_id": current_user.id}
        )
        
        for i, (chunk_content, chunk_id) in enumerate(zip(processed_data["chunks"], chunk_ids)):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_content,
                embedding_id=chunk_id,
                tokens=len(chunk_content.split())
            )
            db.add(chunk)
        
        document.processing_status = "completed"
        await db.commit()
        await db.refresh(document)
        
        return document
    
    except Exception as e:
        if 'document' in locals():
            document.processing_status = "failed"
            document.error_message = str(e)
            await db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )


@router.get("/", response_model=List[DocumentListResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document)
        .options(selectinload(Document.chunks))
        .where(Document.id == document_id, Document.owner_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.owner_id == current_user.id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    embedding_service = EmbeddingService()
    embedding_service.delete_document_embeddings(str(document_id))
    
    await db.delete(document)
    await db.commit()
    
    return {"message": "Document deleted successfully"}