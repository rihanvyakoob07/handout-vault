from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    is_admin: bool
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UploadResponse(BaseModel):
    document_id: str
    version_id: str
    version_number: int

class DocumentVersionOut(BaseModel):
    id: str
    version_number: int
    filename: str
    size: int
    checksum: str
    uploaded_by: str
    created_at: datetime
    changelog: Optional[str] = None

class DocumentOut(BaseModel):
    id: str
    title: str
    subject: Optional[str]
    owner_id: str
    created_at: datetime
    current_version_id: Optional[str]
    versions: List[DocumentVersionOut] = []
