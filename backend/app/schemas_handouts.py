# backend/app/schemas_handouts.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class HandoutVersionOut(BaseModel):
    id: str
    version_number: int
    filename: str
    size: int
    checksum: str
    uploaded_by: str
    created_at: datetime
    changelog: Optional[str] = None

class HandoutOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    created_at: datetime
    current_version_id: Optional[str]
    versions: List[HandoutVersionOut] = []
