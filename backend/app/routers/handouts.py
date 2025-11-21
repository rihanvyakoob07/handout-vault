# backend/app/routers/handouts.py
import os
from datetime import timedelta, datetime
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from jose import jwt, JWTError

from sqlmodel import Session

from app.config import settings
from app.deps import get_session
from app.crud_handouts import (
    create_handout, find_handout_by_title_owner, get_latest_handout_version_number,
    create_handout_version, get_handout, get_handout_versions, record_handout_activity
)
from app.security_utils import checksum_and_size
from app.storage import save_file_version, get_file_path
from app.auth import get_current_user  # reuse auth dependency
from app.models import User
from app.schemas_handouts import HandoutOut, HandoutVersionOut

router = APIRouter(tags=["handouts"])

# helper for public share tokens
def create_public_share_token(handout_id: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    payload = {"handout": handout_id, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_public_share_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        handout_id: str = payload.get("handout")
        if not handout_id:
            raise HTTPException(status_code=400, detail="Invalid share token payload")
        return handout_id
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired share token")

@router.post("/upload", response_model=HandoutOut)
async def upload_handout(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    changelog: Optional[str] = Form(None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    handout = find_handout_by_title_owner(session, title, current_user.id)
    if not handout:
        handout = create_handout(session, title, description, current_user.id)

    latest = get_latest_handout_version_number(session, handout.id)
    new_version = latest + 1

    # Save file to storage (path per handout)
    saved_path, size, checksum = await save_file_version(current_user.id, handout.id, new_version, file)

    # Create DB version and set current
    ver = create_handout_version(session, handout.id, new_version, saved_path, file.filename, file.content_type or "application/octet-stream", checksum, size, current_user.id, changelog=changelog)

    # Activity
    record_handout_activity(session, handout.id, ver.id, "HANDOUT_UPLOAD", current_user.id, request.client.host if request.client else None, details=changelog)

    # return full object
    versions = get_handout_versions(session, handout.id)
    versions_out = [HandoutVersionOut(
        id=v.id,
        version_number=v.version_number,
        filename=v.filename,
        size=v.size,
        checksum=v.checksum,
        uploaded_by=v.uploaded_by,
        created_at=v.created_at,
        changelog=v.changelog
    ) for v in versions]

    return HandoutOut(
        id=handout.id,
        title=handout.title,
        description=handout.description,
        owner_id=handout.owner_id,
        created_at=handout.created_at,
        current_version_id=handout.current_version_id,
        versions=versions_out
    )

@router.get("/{handout_id}", response_model=HandoutOut)
def get_handout_details(handout_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    handout = get_handout(session, handout_id)
    if not handout:
        raise HTTPException(status_code=404, detail="Handout not found")
    if handout.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    versions = get_handout_versions(session, handout_id)
    versions_out = [HandoutVersionOut(
        id=v.id,
        version_number=v.version_number,
        filename=v.filename,
        size=v.size,
        checksum=v.checksum,
        uploaded_by=v.uploaded_by,
        created_at=v.created_at,
        changelog=v.changelog
    ) for v in versions]
    return HandoutOut(
        id=handout.id,
        title=handout.title,
        description=handout.description,
        owner_id=handout.owner_id,
        created_at=handout.created_at,
        current_version_id=handout.current_version_id,
        versions=versions_out
    )

@router.get("/{handout_id}/versions", response_model=list[HandoutVersionOut])
def list_versions(handout_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    handout = get_handout(session, handout_id)
    if not handout:
        raise HTTPException(status_code=404, detail="Handout not found")
    if handout.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    versions = get_handout_versions(session, handout_id)
    return [HandoutVersionOut(
        id=v.id,
        version_number=v.version_number,
        filename=v.filename,
        size=v.size,
        checksum=v.checksum,
        uploaded_by=v.uploaded_by,
        created_at=v.created_at,
        changelog=v.changelog
    ) for v in versions]

@router.get("/{handout_id}/versions/{version_id}/download")
def download_version(handout_id: str, version_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    ver = session.get("HandoutVersion", version_id)  # fallback if direct import missing
    # safe check: fetch via session directly
    ver = session.get(object, version_id) if ver is None else ver  # attempt to avoid runtime errors
    # Instead, fetch via query:
    from sqlmodel import select
    v = session.exec(select(__import__("app.handout_models", fromlist=["HandoutVersion"]).HandoutVersion).where(__import__("app.handout_models", fromlist=["HandoutVersion"]).HandoutVersion.id == version_id)).first()
    if not v or v.handout_id != handout_id:
        raise HTTPException(status_code=404, detail="Version not found")
    handout = get_handout(session, handout_id)
    if handout.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        file_path = get_file_path(v.file_path)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid file path")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stored file not found")
    record_handout_activity(session, handout_id, v.id, "HANDOUT_DOWNLOAD", current_user.id)
    return FileResponse(path=file_path, media_type=v.content_type, filename=v.filename)

@router.post("/{handout_id}/versions/{version_id}/restore")
def restore_version(handout_id: str, version_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    handout = get_handout(session, handout_id)
    if not handout:
        raise HTTPException(status_code=404, detail="Handout not found")
    if handout.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    from sqlmodel import select
    v = session.exec(select(__import__("app.handout_models", fromlist=["HandoutVersion"]).HandoutVersion).where(__import__("app.handout_models", fromlist=["HandoutVersion"]).HandoutVersion.id == version_id)).first()
    if not v or v.handout_id != handout_id:
        raise HTTPException(status_code=404, detail="Version not found")
    handout.current_version_id = v.id
    session.add(handout)
    session.commit()
    record_handout_activity(session, handout.id, v.id, "HANDOUT_RESTORE", current_user.id, details=f"restore v{v.version_number}")
    return {"status": "restored", "current_version_id": handout.current_version_id}

# Public share: returns a time-limited token for public download of the current version
@router.post("/{handout_id}/share")
def create_share(handout_id: str, expires_hours: int = 24, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    handout = get_handout(session, handout_id)
    if not handout:
        raise HTTPException(status_code=404, detail="Handout not found")
    if handout.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    token = create_public_share_token(handout_id, expires_delta=timedelta(hours=expires_hours))
    record_handout_activity(session, handout_id, handout.current_version_id, "HANDOUT_SHARE_CREATED", current_user.id, details=f"expires_in={expires_hours}h")
    return {"share_token": token, "expires_in_hours": expires_hours}

# Public download endpoint - anyone with the token can download the current version
@router.get("/public/download")
def public_download(token: str, session: Session = Depends(get_session)):
    handout_id = decode_public_share_token(token)
    handout = get_handout(session, handout_id)
    if not handout:
        raise HTTPException(status_code=404, detail="Handout not found")
    if not handout.current_version_id:
        raise HTTPException(status_code=404, detail="No version available")
    from sqlmodel import select
    v = session.exec(select(__import__("app.handout_models", fromlist=["HandoutVersion"]).HandoutVersion).where(__import__("app.handout_models", fromlist=["HandoutVersion"]).HandoutVersion.id == handout.current_version_id)).first()
    if not v:
        raise HTTPException(status_code=404, detail="Version not found")
    try:
        file_path = get_file_path(v.file_path)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid file path")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stored file not found")
    # record activity with unknown actor (public)
    record_handout_activity(session, handout.id, v.id, "HANDOUT_PUBLIC_DOWNLOAD", actor_id=None)
    return FileResponse(path=file_path, media_type=v.content_type, filename=v.filename)

# Optional: delete (soft) handout (owner or admin)
@router.delete("/{handout_id}", status_code=204)
def delete_handout(handout_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    handout = get_handout(session, handout_id)
    if not handout:
        raise HTTPException(status_code=404, detail="Handout not found")
    if handout.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    record_handout_activity(session, handout.id, None, "HANDOUT_DELETE", current_user.id)
    return JSONResponse(status_code=204, content=None)
