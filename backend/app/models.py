from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4

def gen_uuid() -> str:
    return str(uuid4())

class User(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    documents: List["Document"] = Relationship(back_populates="owner")


class Document(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    title: str = Field(index=True)
    subject: Optional[str] = None
    owner_id: Optional[str] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    current_version_id: Optional[str] = None

    owner: Optional[User] = Relationship(back_populates="documents")
    versions: List["DocumentVersion"] = Relationship(back_populates="document")


class DocumentVersion(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    document_id: str = Field(foreign_key="document.id", index=True)
    version_number: int
    file_path: str  # local filesystem path
    filename: str
    content_type: str
    checksum: str
    size: int
    uploaded_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    changelog: Optional[str] = None

    document: Optional[Document] = Relationship(back_populates="versions")


class ActivityLog(SQLModel, table=True):
    id: str = Field(default_factory=gen_uuid, primary_key=True)
    document_id: Optional[str] = Field(default=None, foreign_key="document.id")
    version_id: Optional[str] = None
    action: str  # UPLOAD, RESTORE, DOWNLOAD, DELETE
    actor_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
