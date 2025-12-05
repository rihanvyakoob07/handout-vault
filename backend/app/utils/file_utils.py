# backend/app/utils/file_utils.py
import os, hashlib, aiofiles, mimetypes
from app.config import Settings

settings = Settings()

ALLOWED_TYPES = ["application/pdf", 
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                 "application/vnd.openxmlformats-officedocument.presentationml.presentation"]

async def save_file(uid, hid, version, file):
    mime_type = file.content_type
    if mime_type not in ALLOWED_TYPES:
        raise Exception("Unsupported file type")

    size = 0
    sha = hashlib.sha256()

    folder = f"{settings.STORAGE_PATH}/{uid}/{hid}/v{version}/"
    os.makedirs(folder, exist_ok=True)
    full_path = f"{folder}{file.filename}"

    async with aiofiles.open(full_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            sha.update(chunk)
            await f.write(chunk)

    await file.seek(0)

    return full_path, sha.hexdigest(), size, mime_type
