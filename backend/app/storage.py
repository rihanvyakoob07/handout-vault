import os
import pathlib
from app.config import settings
from typing import Tuple
from app.security_utils import save_upload_to_disk, checksum_and_size
from fastapi import UploadFile, HTTPException

ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".txt", ".jpg", ".jpeg", ".png"
}

ALLOWED_MIME_PREFIXES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "image/jpeg",
    "image/png",
}

def ensure_storage_base():
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

def secure_filename(filename: str) -> str:
    # basic sanitation - remove path parts and unsafe chars
    import re
    name = pathlib.Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name

async def save_file_version(user_id: str, document_id: str, version_number: int, file: UploadFile) -> Tuple[str, int, str]:
    """
    Validate file, compute checksum & size, save into storage path and return (saved_path, size, checksum)
    """
    ensure_storage_base()
    fn = secure_filename(file.filename)
    ext = pathlib.Path(fn).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File extension not allowed")

    # MIME check (best-effort)
    if not any(file.content_type.startswith(prefix.split("/")[0]) or file.content_type in ALLOWED_MIME_PREFIXES for prefix in ALLOWED_MIME_PREFIXES):
        # Not strictly blocking here; could leverage python-magic for deeper sniffing
        pass

    checksum, size = await checksum_and_size(file)
    if size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")

    rel_path = f"{user_id}/{document_id}/v{version_number}/{fn}"
    abs_path = os.path.join(settings.STORAGE_PATH, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    # Save to disk
    await save_upload_to_disk(file, abs_path)

    return abs_path, size, checksum

def get_file_path(file_path: str) -> str:
    """
    Sanity-check that the path is inside storage root and return absolute path.
    """
    storage_root = os.path.abspath(settings.STORAGE_PATH)
    requested = os.path.abspath(file_path)
    if not requested.startswith(storage_root):
        raise ValueError("Invalid path")
    return requested
