# backend/app/handout_models.py
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4

def gen_uuid() -> str:
    return str(uuid4())

class Handout(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    owner_id: Optional[str] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_version_id: Optional[str] = None

    owner: Optional["User"] = Relationship(sa_relationship_kwargs={"lazy": "select"}, back_populates="handouts")
    versions: List["HandoutVersion"] = Relationship(back_populates="handout")


class HandoutVersion(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    handout_id: str = Field(foreign_key="handout.id", index=True)
    version_number: int
    file_path: str
    filename: str
    content_type: str
    checksum: str
    size: int
    uploaded_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    changelog: Optional[str] = None

    handout: Optional[Handout] = Relationship(back_populates="versions")
