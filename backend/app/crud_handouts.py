# backend/app/crud_handouts.py
from typing import Optional, List, Tuple
from sqlmodel import select, func, Session
from app.handout_models import Handout, HandoutVersion
from app.models import User
from app.crud import record_activity  # reuse activity logging
from app.storage import save_file_version  # reuse storage helpers
from app.security_utils import checksum_and_size
from fastapi import UploadFile, HTTPException

# Handout CRUD
def create_handout(session: Session, title: str, description: Optional[str], owner_id: str) -> Handout:
    handout = Handout(title=title, description=description, owner_id=owner_id)
    session.add(handout)
    session.commit()
    session.refresh(handout)
    return handout

def get_handout(session: Session, handout_id: str) -> Optional[Handout]:
    return session.get(Handout, handout_id)

def find_handout_by_title_owner(session: Session, title: str, owner_id: str) -> Optional[Handout]:
    return session.exec(select(Handout).where(Handout.title == title, Handout.owner_id == owner_id)).first()

# Versions
def get_handout_versions(session: Session, handout_id: str) -> List[HandoutVersion]:
    return session.exec(select(HandoutVersion).where(HandoutVersion.handout_id == handout_id).order_by(HandoutVersion.version_number.desc())).all()

def get_latest_handout_version_number(session: Session, handout_id: str) -> int:
    result = session.exec(select(func.max(HandoutVersion.version_number)).where(HandoutVersion.handout_id == handout_id)).one()
    return result or 0

def create_handout_version(session: Session, handout_id: str, version_number: int, file_path: str, filename: str, content_type: str, checksum: str, size: int, uploaded_by: str, changelog: Optional[str] = None) -> HandoutVersion:
    ver = HandoutVersion(
        handout_id=handout_id,
        version_number=version_number,
        file_path=file_path,
        filename=filename,
        content_type=content_type,
        checksum=checksum,
        size=size,
        uploaded_by=uploaded_by,
        changelog=changelog
    )
    session.add(ver)
    session.commit()
    session.refresh(ver)

    # set current version on handout
    handout = session.get(Handout, handout_id)
    handout.current_version_id = ver.id
    session.add(handout)
    session.commit()
    session.refresh(handout)

    # activity log
    record_activity(session, handout_id, ver.id, "HANDOUT_UPLOAD", uploaded_by, details=changelog)
    return ver

def record_handout_activity(session: Session, handout_id: Optional[str], version_id: Optional[str], action: str, actor_id: Optional[str], ip: Optional[str] = None, details: Optional[str] = None):
    return record_activity(session, handout_id, version_id, action, actor_id, ip, details)
