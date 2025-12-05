# backend/app/services/version_service.py
from sqlmodel import Session, select
from app.models.version import HandoutVersion

def simple_summary(text: str):
    text = text or ""
    return text[:250] + "..." if len(text) > 250 else text

def get_next_version(session: Session, handout_id: str):
    last = session.exec(
        select(HandoutVersion)
        .where(HandoutVersion.handout_id == handout_id)
        .order_by(HandoutVersion.version.desc())
    ).first()
    return 1 if not last else last.version + 1

def create_version(session: Session, handout, file_path, mime, size, checksum, user_email):
    vnum = get_next_version(session, handout.id)
    summary = simple_summary(f"Uploaded by {user_email}")

    v = HandoutVersion(
        handout_id=handout.id,
        version=vnum,
        file_path=file_path,
        file_type=mime,
        file_size=size,
        checksum=checksum,
        summary=summary,
        uploaded_by=user_email
    )

    handout.current_version = vnum

    session.add(v)
    session.add(handout)
    session.commit()
    session.refresh(v)

    return v
