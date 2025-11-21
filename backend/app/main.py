import os
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import Optional, List
from app.config import settings
from app.deps import init_db, get_session
from app.crud import create_user, get_user_by_email, create_document, find_document_by_title_owner, get_latest_version_number, create_version, record_activity, get_document, get_versions
from app.security_utils import verify_password, checksum_and_size
from app.schemas import LoginRequest, UploadResponse, DocumentOut, DocumentVersionOut
from app.auth import create_access_token, get_current_user, require_admin
from app.storage import save_file_version, get_file_path
from app.models import User, DocumentVersion, Document

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # create directories & DB
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    init_db()

# --------- AUTH ROUTES ----------
@app.post("/auth/register", status_code=201)
def register(data: LoginRequest, session: Session = Depends(get_session)):
    existing = get_user_by_email(session, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = create_user(session, data.email, data.password)
    return {"message": "user_created", "user_id": user.id}

@app.post("/auth/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = get_user_by_email(session, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "is_admin": user.is_admin}}

# --------- DOCUMENTS & VERSIONING ----------
@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    request: Request,
    title: str = Form(...),
    subject: Optional[str] = Form(None),
    changelog: Optional[str] = Form(None),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Basic server-side validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    # Reuse document if exists for same owner + title, else create new
    doc = find_document_by_title_owner(session, title, current_user.id)
    if doc is None:
        doc = create_document(session, title, subject, current_user.id)

    latest = get_latest_version_number(session, doc.id)
    new_version = latest + 1

    # Save file to local storage
    saved_path, size, checksum = await save_file_version(current_user.id, doc.id, new_version, file)

    # Create DB version
    ver = create_version(session, doc.id, new_version, saved_path, file.filename, file.content_type, checksum, size, current_user.id, changelog=changelog)
    record_activity(session, doc.id, ver.id, "UPLOAD", current_user.id, request.client.host if request.client else None, details=changelog)

    return UploadResponse(document_id=doc.id, version_id=ver.id, version_number=new_version)

@app.get("/documents/{doc_id}", response_model=DocumentOut)
def get_document_details(doc_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    doc = get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    versions = get_versions(session, doc_id)
    versions_out = [DocumentVersionOut(
        id=v.id,
        version_number=v.version_number,
        filename=v.filename,
        size=v.size,
        checksum=v.checksum,
        uploaded_by=v.uploaded_by,
        created_at=v.created_at,
        changelog=v.changelog
    ) for v in versions]
    return DocumentOut(
        id=doc.id,
        title=doc.title,
        subject=doc.subject,
        owner_id=doc.owner_id,
        created_at=doc.created_at,
        current_version_id=doc.current_version_id,
        versions=versions_out
    )

@app.get("/documents/{doc_id}/versions", response_model=List[DocumentVersionOut])
def list_versions(doc_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    doc = get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    versions = get_versions(session, doc_id)
    return [DocumentVersionOut(
        id=v.id,
        version_number=v.version_number,
        filename=v.filename,
        size=v.size,
        checksum=v.checksum,
        uploaded_by=v.uploaded_by,
        created_at=v.created_at,
        changelog=v.changelog
    ) for v in versions]

@app.get("/documents/{doc_id}/versions/{version_id}/download")
def download_version(doc_id: str, version_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    ver = session.get(DocumentVersion, version_id)
    if not ver or ver.document_id != doc_id:
        raise HTTPException(status_code=404, detail="Version not found")
    doc = get_document(session, doc_id)
    if doc.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    # Validate path and return file
    try:
        file_path = get_file_path(ver.file_path)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid file path")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Stored file not found")
    record_activity(session, doc_id, ver.id, "DOWNLOAD", current_user.id)
    return FileResponse(path=file_path, media_type=ver.content_type, filename=ver.filename)

@app.post("/documents/{doc_id}/versions/{version_id}/restore")
def restore_version(doc_id: str, version_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    doc = get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    ver = session.get(DocumentVersion, version_id)
    if not ver or ver.document_id != doc_id:
        raise HTTPException(status_code=404, detail="Version not found")
    # Set current version
    doc.current_version_id = ver.id
    session.add(doc)
    session.commit()
    record_activity(session, doc.id, ver.id, "RESTORE", current_user.id, details=f"restore v{ver.version_number}")
    return {"status": "restored", "current_version_id": doc.current_version_id}

@app.delete("/documents/{doc_id}", status_code=204)
def delete_document(doc_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    doc = get_document(session, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Soft delete: log delete action. Actual file deletion can be admin-only or scheduled.
    record_activity(session, doc.id, None, "DELETE", current_user.id)
    return JSONResponse(status_code=204, content=None)

@app.get("/")
def root():
    return {"status": "ok", "app": settings.APP_NAME}
