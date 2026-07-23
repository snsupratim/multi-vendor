import uuid
from datetime import datetime, timezone
from loguru import logger

from repositories.document_repository import DocumentRepository
from services.pdf_service import PDFService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.vector_store_service import VectorStoreService

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

        document_id = str(uuid.uuid4())
        text = PDFService.extract_text(file_path)
        chunks = ChunkService.split(text)
        rows = []

        for idx, chunk in enumerate(chunks):
            embedding = EmbeddingService.get_embedding(chunk)
            rows.append({
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
            })

        VectorStoreService.bulk_insert(rows)

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
                    "created_at": datetime.now(timezone.utc)
                }
            )
        )

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

    @staticmethod
    async def ingest_json_document(
        payload,
        uploaded_by: str
    ):
        
        document_id = str(uuid.uuid4())
        text = payload.pageContent
        chunks = ChunkService.split(text)
        rows = []
        
        module_name = payload.metadata.get("module")
        sub_module = payload.metadata.get("parentModule") or payload.metadata.get("sub_module")
        source = payload.metadata.get("moduleLink", "API")
        file_name = f"JSON - {module_name}" if module_name else "JSON Upload"

        for idx, chunk in enumerate(chunks):
            embedding = EmbeddingService.get_embedding(chunk)
            rows.append({
                "id": str(uuid.uuid4()),
                "vendor_id": payload.vendor_id,
                "workspace_id": payload.workspace_id,
                "document_id": document_id,
                "chunk_id": idx,
                "content": chunk,
                "embedding": embedding,
                "file_name": file_name,
                "document_type": "JSON",
                "module": module_name,
                "sub_module": sub_module,
                "metadata": payload.metadata,
                "source": source
            })

        VectorStoreService.bulk_insert(rows)

        await (
            DocumentRepository
            .create_document(
                {
                    "document_id": document_id,
                    "vendor_id": payload.vendor_id,
                    "workspace_id": payload.workspace_id,
                    "file_name": file_name,
                    "document_type": "JSON",
                    "chunk_count": len(chunks),
                    "uploaded_by": uploaded_by,
                    "created_at": datetime.now(timezone.utc)
                }
            )
        )

        logger.info(
            f"JSON Document uploaded "
            f"workspace={payload.workspace_id} "
            f"document={document_id} "
            f"chunks={len(chunks)}"
        )

        return {
            "document_id": document_id,
            "chunks_created": len(chunks)
        }

    @staticmethod
    async def ingest_sql_schema(
        payload,
        uploaded_by: str
    ):
        
        document_id = str(uuid.uuid4())
        
        full_content = f"Table Name: {payload.table_name}\nDescription: {payload.description}\nSchema DDL:\n{payload.schema_ddl}\nRelationships:\n{payload.relationships}"
        
        embedding = EmbeddingService.get_embedding(full_content)
        
        row = {
            "id": str(uuid.uuid4()),
            "vendor_id": payload.vendor_id,
            "workspace_id": payload.workspace_id,
            "document_id": document_id,
            "chunk_id": 0,
            "content": full_content,
            "embedding": embedding,
            "file_name": f"SQL Schema - {payload.table_name}",
            "document_type": "SQL_SCHEMA",
            "module": None,
            "sub_module": None,
            "metadata": {
                "table_name": payload.table_name,
                "description": payload.description,
                "relationships": payload.relationships
            },
            "source": "API"
        }

        VectorStoreService.bulk_insert([row])

        await (
            DocumentRepository
            .create_document(
                {
                    "document_id": document_id,
                    "vendor_id": payload.vendor_id,
                    "workspace_id": payload.workspace_id,
                    "file_name": f"SQL Schema - {payload.table_name}",
                    "document_type": "SQL_SCHEMA",
                    "chunk_count": 1,
                    "uploaded_by": uploaded_by,
                    "created_at": datetime.now(timezone.utc)
                }
            )
        )

        logger.info(
            f"SQL Schema uploaded "
            f"workspace={payload.workspace_id} "
            f"table={payload.table_name}"
        )

        return {
            "document_id": document_id,
            "chunks_created": 1
        }
