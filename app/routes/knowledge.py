from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeResponse,
    KnowledgeUpdate,
)
from app.services.knowledge import (
    create_knowledge,
    delete_knowledge,
    get_knowledge,
    get_user_knowledge,
    knowledge_response,
    update_knowledge,
)
from app.services.knowledge import knowledge_response

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"]
)


@router.post(
    "",
    response_model=KnowledgeResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: KnowledgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    knowledge = await create_knowledge(
        db,
        data,
        current_user
    )

    return knowledge_response(knowledge)



@router.get(
    "",
    response_model=list[KnowledgeResponse]
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    knowledge_items = await get_user_knowledge(
        db,
        current_user
    )

    return [
        knowledge_response(item)
        for item in knowledge_items
    ]
@router.get(
    "/{knowledge_id}",
    response_model=KnowledgeResponse
)
async def get_one(
    knowledge_id: str,
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

    return knowledge


@router.put(
    "/{knowledge_id}",
    response_model=KnowledgeResponse
)
async def update(
    knowledge_id: str,
    data: KnowledgeUpdate,
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

    knowledge = await update_knowledge(
        db,
        knowledge,
        data
    )

    return knowledge_response(knowledge)


@router.delete(
    "/{knowledge_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(
    knowledge_id: str,
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

    await delete_knowledge(db, knowledge)