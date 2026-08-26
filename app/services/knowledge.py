from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import KnowledgeItem, Tag, User
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate


async def get_or_create_tag(
    db: AsyncSession,
    tag_name: str
) -> Tag:

    tag_name = tag_name.strip()

    tag = await db.scalar(
        select(Tag).where(Tag.name == tag_name)
    )

    if tag:
        return tag

    tag = Tag(name=tag_name)

    db.add(tag)

    await db.flush()

    return tag


async def create_knowledge(
    db: AsyncSession,
    data: KnowledgeCreate,
    user: User
) -> KnowledgeItem:

    knowledge = KnowledgeItem(
        user_id=user.id,
        type=data.type.upper(),
        title=data.title,
        description=data.description,
        content=data.content,
    )

    for tag_name in data.tags:

        if tag_name.strip():

            tag = await get_or_create_tag(
                db,
                tag_name
            )

            knowledge.tags.append(tag)

    db.add(knowledge)

    await db.commit()
    await db.refresh(knowledge)

    return knowledge


async def get_user_knowledge(
    db: AsyncSession,
    user: User
) -> list[KnowledgeItem]:

    result = await db.scalars(
        select(KnowledgeItem)
        .where(
            KnowledgeItem.user_id == user.id
        )
        .order_by(
            KnowledgeItem.created_at.desc()
        )
    )

    return list(result.all())


async def get_knowledge(
    db: AsyncSession,
    knowledge_id: str,
    user: User
) -> KnowledgeItem | None:

    return await db.scalar(
        select(KnowledgeItem)
        .where(
            KnowledgeItem.id == knowledge_id,
            KnowledgeItem.user_id == user.id
        )
    )


async def update_knowledge(
    db: AsyncSession,
    knowledge: KnowledgeItem,
    data: KnowledgeUpdate
) -> KnowledgeItem:

    if data.title is not None:
        knowledge.title = data.title

    if data.description is not None:
        knowledge.description = data.description

    if data.content is not None:
        knowledge.content = data.content

    # Update tags only if tags were provided
    if data.tags is not None:

        knowledge.tags.clear()

        for tag_name in data.tags:

            if tag_name.strip():

                tag = await get_or_create_tag(
                    db,
                    tag_name
                )

                knowledge.tags.append(tag)

    await db.commit()

    await db.refresh(knowledge)

    return knowledge


async def delete_knowledge(
    db: AsyncSession,
    knowledge: KnowledgeItem
):
    await db.delete(knowledge)

    await db.commit()


def knowledge_response(
    knowledge: KnowledgeItem
) -> dict:

    return {
        "id": knowledge.id,
        "type": knowledge.type,
        "title": knowledge.title,
        "description": knowledge.description,
        "content": knowledge.content,
        "file_url": knowledge.file_url,
        "file_name": knowledge.file_name,
        "mime_type": knowledge.mime_type,
        "tags": [
            tag.name
            for tag in knowledge.tags
        ],
        "created_at": knowledge.created_at,
        "updated_at": knowledge.updated_at,
    }