import hashlib
import aiofiles
from passlib.context import CryptContext
from typing import Tuple
from fastapi import UploadFile

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain_password: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain_password, hashed)

async def checksum_and_size(file: UploadFile) -> Tuple[str, int]:
    """
    Read file in chunks (async) and compute SHA256 checksum and total size.
    This resets file pointer to 0 at the end.
    """
    sha = hashlib.sha256()
    total = 0
    await file.seek(0)
    chunk = await file.read(1024 * 1024)
    while chunk:
        sha.update(chunk)
        total += len(chunk)
        chunk = await file.read(1024 * 1024)
    await file.seek(0)
    return sha.hexdigest(), total

async def save_upload_to_disk(file: UploadFile, target_path: str) -> None:
    """
    Save UploadFile to local disk using aiofiles. Creates directories as needed.
    """
    import os
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    await file.seek(0)
    async with aiofiles.open(target_path, "wb") as f:
        chunk = await file.read(1024 * 1024)
        while chunk:
            await f.write(chunk)
            chunk = await file.read(1024 * 1024)
    await file.seek(0)
