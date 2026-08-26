from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.schemas.todo import (
    TodoCreate,
    TodoResponse,
    TodoUpdate,
)
from app.services.todo import (
    create_todo,
    delete_todo,
    get_todo,
    get_user_todos,
    update_todo,
)


router = APIRouter(
    prefix="/todos",
    tags=["Todos"]
)


@router.post(
    "",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: TodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await create_todo(
        db,
        data,
        current_user
    )


@router.get(
    "",
    response_model=list[TodoResponse]
)
async def get_all(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_user_todos(
        db,
        current_user
    )


@router.get(
    "/{todo_id}",
    response_model=TodoResponse
)
async def get_one(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    todo = await get_todo(
        db,
        todo_id,
        current_user
    )

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return todo


@router.put(
    "/{todo_id}",
    response_model=TodoResponse
)
async def update(
    todo_id: str,
    data: TodoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    todo = await get_todo(
        db,
        todo_id,
        current_user
    )

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    return await update_todo(
        db,
        todo,
        data
    )


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(
    todo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    todo = await get_todo(
        db,
        todo_id,
        current_user
    )

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found"
        )

    await delete_todo(db, todo)