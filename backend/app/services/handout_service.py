# backend/app/services/handout_service.py
from sqlmodel import Session, select
from app.models.handout import Handout

def get_handout_by_id(session: Session, hid: str, owner: str):
    h = session.exec(select(Handout).where(Handout.id == hid)).first()
    if not h:
        raise Exception("Handout not found")
    if h.owner_id != owner:
        raise Exception("Not allowed")
    return h

def get_or_create(session: Session, title: str, owner: str, subject: str = None):
    h = session.exec(
        select(Handout).where(Handout.title == title, Handout.owner_id == owner)
    ).first()

    if h:
        return h

    h = Handout(title=title, owner_id=owner, subject=subject)
    session.add(h)
    session.commit()
    session.refresh(h)
    return h
