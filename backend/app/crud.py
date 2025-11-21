from sqlmodel import select, func
from app.models import User, Document, DocumentVersion, ActivityLog
from sqlmodel import Session
from typing import Optional
from app.security_utils import hash_password

# --- Users ---
def create_user(session: Session, email: str, password: str, is_admin: bool = False) -> User:
    user = User(email=email, hashed_password=hash_password(password), is_admin=is_admin)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()

def get_user_by_id(session: Session, user_id: str) -> Optional[User]:
    return session.get(User, user_id)

# --- Documents & versions ---
def create_document(session: Session, title: str, subject: Optional[str], owner_id: str) -> Document:
    doc = Document(title=title, subject=subject, owner_id=owner_id)
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc

def get_document(session: Session, doc_id: str) -> Optional[Document]:
    return session.get(Document, doc_id)

def find_document_by_title_owner(session: Session, title: str, owner_id: str) -> Optional[Document]:
    return session.exec(select(Document).where(Document.title == title, Document.owner_id == owner_id)).first()

def get_versions(session: Session, doc_id: str):
    return session.exec(select(DocumentVersion).where(DocumentVersion.document_id == doc_id).order_by(DocumentVersion.version_number.desc())).all()

def get_latest_version_number(session: Session, doc_id: str) -> int:
    result = session.exec(select(func.max(DocumentVersion.version_number)).where(DocumentVersion.document_id == doc_id)).one()
    return result or 0

def create_version(session: Session, doc_id: str, version_number: int, file_path: str, filename: str, content_type: str, checksum: str, size: int, uploaded_by: str, changelog: Optional[str] = None) -> DocumentVersion:
    ver = DocumentVersion(
        document_id=doc_id,
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

    # set current version
    doc = session.get(Document, doc_id)
    doc.current_version_id = ver.id
    session.add(doc)
    session.commit()
    session.refresh(doc)

    # activity log
    log = ActivityLog(document_id=doc_id, version_id=ver.id, action="UPLOAD", actor_id=uploaded_by, details=changelog)
    session.add(log)
    session.commit()
    session.refresh(log)

    return ver

def record_activity(session: Session, document_id: Optional[str], version_id: Optional[str], action: str, actor_id: Optional[str], ip: Optional[str] = None, details: Optional[str] = None) -> ActivityLog:
    log = ActivityLog(document_id=document_id, version_id=version_id, action=action, actor_id=actor_id, ip_address=ip, details=details)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
