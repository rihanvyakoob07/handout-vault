from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4


class HandoutVersion(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

    handout_id: str = Field(foreign_key="handout.id")
    version_number: int
    filename: str
    storage_path: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

    # FIXED: symmetrical relationship
    handout: "Handout" = Relationship(back_populates="versions")
