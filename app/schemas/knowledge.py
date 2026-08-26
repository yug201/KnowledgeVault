from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeCreate(BaseModel):
    type: str = Field(min_length=1, max_length=30)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    content: str | None = None
    tags: list[str] = []


class KnowledgeUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )
    description: str | None = None
    content: str | None = None
    tags: list[str] | None = None


class KnowledgeResponse(BaseModel):
    id: str
    type: str
    title: str
    description: str | None
    content: str | None
    file_url: str | None
    file_name: str | None
    mime_type: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime