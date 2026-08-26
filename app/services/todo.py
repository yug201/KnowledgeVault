from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Todo, User
from app.schemas.todo import TodoCreate, TodoUpdate


async def create_todo(
    db: AsyncSession,
    data: TodoCreate,
    user: User
) -> Todo:

    todo = Todo(
        user_id=user.id,
        title=data.title,
        description=data.description,
    )

    db.add(todo)

    await db.commit()
    await db.refresh(todo)

    return todo


async def get_user_todos(
    db: AsyncSession,
    user: User
) -> list[Todo]:

    result = await db.scalars(
        select(Todo)
        .where(Todo.user_id == user.id)
        .order_by(Todo.created_at.desc())
    )

    return list(result.all())


async def get_todo(
    db: AsyncSession,
    todo_id: str,
    user: User
) -> Todo | None:

    return await db.scalar(
        select(Todo)
        .where(
            Todo.id == todo_id,
            Todo.user_id == user.id
        )
    )


async def update_todo(
    db: AsyncSession,
    todo: Todo,
    data: TodoUpdate
) -> Todo:

    if data.title is not None:
        todo.title = data.title

    if data.description is not None:
        todo.description = data.description

    if data.completed is not None:
        todo.completed = data.completed

    await db.commit()
    await db.refresh(todo)

    return todo


async def delete_todo(
    db: AsyncSession,
    todo: Todo
):
    await db.delete(todo)
    await db.commit()