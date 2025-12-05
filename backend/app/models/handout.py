from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4
from typing import List, Optional


class Handout(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    subject: str = Field(index=True)
    title: str
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    latest_version: int = Field(default=1)

    # FIXED: relationship added
    versions: List["HandoutVersion"] = Relationship(back_populates="handout")
