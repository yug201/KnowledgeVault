from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.services.knowledge import get_knowledge
from app.services.storage import upload_file


router = APIRouter(
    prefix="/knowledge",
    tags=["Files"]
)

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "video/mp4",
}

MAX_FILE_SIZE = 10 * 1024 * 1024
@router.post("/{knowledge_id}/file")
async def upload_knowledge_file(
    knowledge_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    knowledge = await get_knowledge(
        db,
        knowledge_id,
        current_user
    )

    if knowledge is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge item not found"
        )
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )
    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 10 MB."
        )
    response = await upload_file(
        file_data,
        file.filename
    )

    knowledge.file_url = response.url
    knowledge.file_name = file.filename
    knowledge.mime_type = file.content_type

    await db.commit()
    await db.refresh(knowledge)

    return {
        "message": "File uploaded successfully",
        "file_url": knowledge.file_url,
        "file_name": knowledge.file_name,
        "mime_type": knowledge.mime_type
    }