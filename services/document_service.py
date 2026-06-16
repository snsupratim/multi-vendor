import uuid

from datetime import (
    datetime,
    timezone
)

from loguru import logger

from repositories.document_repository import (
    DocumentRepository
)

from services.pdf_service import (
    PDFService
)

from services.chunk_service import (
    ChunkService
)

from services.embedding_service import (
    EmbeddingService
)

from services.vector_store_service import (
    VectorStoreService
)


class DocumentService:

    @staticmethod
    async def ingest_document(
        file_path: str,
        file_name: str,
        workspace_id: str,
        vendor_id: str,
        uploaded_by: str
    ):
        
        existing = await (
    DocumentRepository
    .find_by_file_name(
        file_name,
        workspace_id
    )
)

        if existing:
            raise ValueError(
        f"Document '{file_name}' already exists in workspace"
    )

        document_id = str(
            uuid.uuid4()
        )

        text = (
            PDFService.extract_text(
                file_path
            )
        )

        chunks = (
            ChunkService.split(
                text
            )
        )

        rows = []

        for idx, chunk in enumerate(chunks):

            embedding = (
            EmbeddingService.get_embedding(
            chunk
        )
        )

        rows.append(
        {
            "id": str(uuid.uuid4()),
            "vendor_id": vendor_id,
            "workspace_id": workspace_id,
            "document_id": document_id,
            "chunk_id": idx,
            "content": chunk,
            "embedding": embedding,
            "file_name": file_name,
            "document_type": "PDF",
            "module": None,
            "sub_module": None,
            "metadata": {},
            "source": file_name
        }
    )

        VectorStoreService.bulk_insert(
    rows
)
        await (
            DocumentRepository
            .create_document(
                {
                    "document_id": document_id,
                    "vendor_id": vendor_id,
                    "workspace_id": workspace_id,
                    "file_name": file_name,
                    "document_type": "PDF",
                    "chunk_count": len(chunks),
                    "uploaded_by": uploaded_by,
                    "created_at": datetime.now(
                        timezone.utc
                    )
                }
            )
        )
        # SUCCESS LOG HERE
        logger.info(
                f"Document uploaded "
                f"workspace={workspace_id} "
                f"document={document_id} "
                f"chunks={len(chunks)}"
            )
        

        return {
            "document_id": document_id,
            "chunks_created": len(chunks)
        }
    

