import os
import json
import uuid
from fastapi import (
    APIRouter, Depends, Header, UploadFile, File,
    HTTPException, Form
)

router = APIRouter(prefix="/handouts", tags=["handouts"])

# ============================================================
# JSON STORAGE (NO DATABASE)
# ============================================================
DATA_FILE = "handout_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"subjects": {}, "handouts": {}, "versions": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
# STATIC TOKEN AUTH
# ============================================================
STATIC_SECRET = "HANDOUTVAULTSECRET123"

def user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")

    token = authorization.replace("Bearer ", "").strip()
    if token != STATIC_SECRET:
        raise HTTPException(401, "Invalid token")

    return {"user": "local"}


# ============================================================
# UTIL: FILE SAVER
# ============================================================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file: UploadFile):
    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, unique_name)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path


# ============================================================
# LIST ALL SUBJECTS
# ============================================================
@router.get("/subjects")
def get_subjects(user=Depends(user)):
    data = load_data()
    subjects = []

    for subject, handout_ids in data["subjects"].items():
        subjects.append({"id": subject, "count": len(handout_ids)})

    return subjects


# ============================================================
# LIST HANDOUTS INSIDE A SUBJECT
# ============================================================
@router.get("/subject/{subject_name}")
def get_handouts(subject_name: str, user=Depends(user)):
    data = load_data()

    if subject_name not in data["subjects"]:
        return []

    result = []
    for hid in data["subjects"][subject_name]:
        result.append(data["handouts"][hid])

    return result


# ============================================================
# UPLOAD HANDOUT OR NEW VERSION
# ============================================================
@router.post("/upload")
async def upload_handout(
    subject: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(user),
):
    data = load_data()

    # ensure subject exists
    if subject not in data["subjects"]:
        data["subjects"][subject] = []

    # save file
    file_path = save_file(file)

    # check if handout already exists
    existing_id = None
    for hid, hdata in data["handouts"].items():
        if hdata["subject"] == subject and hdata["title"].lower() == title.lower():
            existing_id = hid
            break

    if existing_id:
        # Add version
        handout = data["handouts"][existing_id]
        new_version = handout["latest_version"] + 1

        version_id = f"{existing_id}_v{new_version}"
        data["versions"][version_id] = {
            "version_id": version_id,
            "handout_id": existing_id,
            "version": new_version,
            "file_path": file_path
        }

        handout["latest_version"] = new_version
        save_data(data)

        return {"status": "ok", "message": "New version added", "handout_id": existing_id}

    # create new handout
    new_id = uuid.uuid4().hex

    data["handouts"][new_id] = {
        "id": new_id,
        "title": title,
        "subject": subject,
        "latest_version": 1
    }

    data["subjects"][subject].append(new_id)

    # version 1
    version_id = f"{new_id}_v1"
    data["versions"][version_id] = {
        "version_id": version_id,
        "handout_id": new_id,
        "version": 1,
        "file_path": file_path
    }

    save_data(data)

    return {"status": "ok", "message": "Handout uploaded", "handout_id": new_id}


# ============================================================
# LIST VERSIONS OF A HANDOUT
# ============================================================
@router.get("/{handout_id}/versions")
def get_versions(handout_id: str, user=Depends(user)):
    data = load_data()

    result = []
    for vid, vdata in data["versions"].items():
        if vdata["handout_id"] == handout_id:
            result.append(vdata)

    # newest first
    result.sort(key=lambda x: x["version"], reverse=True)

    return result


# ============================================================
# GET SPECIFIC VERSION FILE INFO
# ============================================================
@router.get("/{handout_id}/version/{version_number}")
def get_version_file(handout_id: str, version_number: int, user=Depends(user)):
    data = load_data()
    version_id = f"{handout_id}_v{version_number}"

    if version_id not in data["versions"]:
        raise HTTPException(404, "Version does not exist")

    return {"file_path": data["versions"][version_id]["file_path"]}
