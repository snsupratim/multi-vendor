import os

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Form,
    Depends
)

from core.dependencies import (
    get_current_user
)

from services.document_service import (
    DocumentService
)

from schemas.document_schema import (
    JsonDocumentRequest
)

UPLOAD_DIR = "uploads"

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_document(
    workspace_id: str = Form(...),
    vendor_id: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(
        get_current_user
    )
):

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )

    file_path = (
        f"{UPLOAD_DIR}/{file.filename}"
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        buffer.write(
            await file.read()
        )

    try:

        return await (
        DocumentService
        .ingest_document(
            file_path=file_path,
            file_name=file.filename,
            workspace_id=workspace_id,
            vendor_id=vendor_id,
            uploaded_by=user["sub"]
        )
    )
    except ValueError as e:

        raise HTTPException(
        status_code=400,
        detail=str(e)
    )

@router.post("/upload/json")
async def upload_json_document(
    payload: JsonDocumentRequest,
    user=Depends(get_current_user)
):
    try:
        return await DocumentService.ingest_json_document(
            payload=payload,
            uploaded_by=user["sub"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )