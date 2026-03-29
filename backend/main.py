import io
import os
import secrets
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
from run_pipeline import run_pipeline


app = FastAPI(title="Insurance Schematic Generator API")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "28800"))
UPLOAD_TTL_SECONDS = int(os.getenv("UPLOAD_TTL_SECONDS", "1800"))
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@dataclass
class UploadSession:
    file_path: str
    file_name: str
    created_at: float
    validation_result: dict


auth_sessions: Dict[str, float] = {}
upload_sessions: Dict[str, UploadSession] = {}
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "schematic_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class GenerateRequest(BaseModel):
    upload_id: str
    account_name_override: Optional[str] = None
    warning_answers: Dict[str, str] = Field(default_factory=dict)


def _cleanup_expired_state() -> None:
    now = time.time()

    expired_tokens = [token for token, expires_at in auth_sessions.items() if expires_at <= now]
    for token in expired_tokens:
        auth_sessions.pop(token, None)

    expired_uploads = [
        upload_id
        for upload_id, session in upload_sessions.items()
        if session.created_at + UPLOAD_TTL_SECONDS <= now
    ]
    for upload_id in expired_uploads:
        session = upload_sessions.pop(upload_id, None)
        if session and os.path.exists(session.file_path):
            os.remove(session.file_path)


def _create_upload_session(file_name: str, content: bytes, validation_result: dict) -> str:
    upload_id = uuid.uuid4().hex
    file_path = os.path.join(UPLOAD_DIR, f"{upload_id}.xlsx")
    with open(file_path, "wb") as handle:
        handle.write(content)

    upload_sessions[upload_id] = UploadSession(
        file_path=file_path,
        file_name=file_name,
        created_at=time.time(),
        validation_result=validation_result,
    )
    return upload_id


def _pop_upload_session(upload_id: str) -> UploadSession:
    _cleanup_expired_state()
    session = upload_sessions.pop(upload_id, None)
    if not session:
        raise HTTPException(status_code=404, detail="Upload session expired. Please upload the file again.")
    return session


def _require_auth(authorization: Optional[str] = Header(default=None)) -> str:
    _cleanup_expired_state()

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")

    token = authorization.removeprefix("Bearer ").strip()
    expires_at = auth_sessions.get(token)
    if not expires_at or expires_at <= time.time():
        auth_sessions.pop(token, None)
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    return token


def _build_carrier_merges(validation_flags: list, warning_answers: Dict[str, str]) -> Dict[str, str]:
    merges: Dict[str, str] = {}
    for flag in validation_flags:
        if flag["id"] != "W04":
            continue
        answer = warning_answers.get(flag["key"], "").strip().lower()
        if answer not in {"yes", "no"}:
            raise HTTPException(status_code=400, detail=f"Please answer the confirmation for {flag['message']}")
        if answer == "yes":
            name_a, name_b = flag.get("metadata", {}).get("merge_candidates", [None, None])
            if name_a and name_b:
                merges[name_b] = name_a
    return merges


@app.post("/api/login")
async def login(req: LoginRequest):
    _cleanup_expired_state()

    if req.username != ADMIN_USERNAME or req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = secrets.token_urlsafe(32)
    auth_sessions[token] = time.time() + SESSION_TTL_SECONDS
    return {"status": "success", "token": token, "expires_in": SESSION_TTL_SECONDS}


@app.post("/api/logout")
async def logout(token: str = Depends(_require_auth)):
    auth_sessions.pop(token, None)
    return {"status": "success"}


@app.get("/api/session")
async def session_status(_: str = Depends(_require_auth)):
    return {"status": "ok"}


@app.post("/api/validate")
async def validate_excel(file: UploadFile = File(...), _: str = Depends(_require_auth)):
    _cleanup_expired_state()

    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Please upload a valid .xlsx file.")

    content = await file.read()
    temp_path = os.path.join(UPLOAD_DIR, f"validate-{uuid.uuid4().hex}.xlsx")
    with open(temp_path, "wb") as handle:
        handle.write(content)

    try:
        result = run_pipeline(temp_path, confirmed_warnings=False, render=False)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    response = {
        "status": result["status"],
        "report": result["report"],
        "flags": result.get("flags", []),
        "file_name": file.filename,
    }

    if result["status"] != "blocked":
        response["upload_id"] = _create_upload_session(file.filename, content, result)

    return response


@app.post("/api/generate")
async def generate_pptx(req: GenerateRequest, _: str = Depends(_require_auth)):
    session = _pop_upload_session(req.upload_id)

    try:
        validation_flags = session.validation_result.get("flags", [])
        required_account_name = any(flag["id"] == "W03" for flag in validation_flags)
        if required_account_name and not (req.account_name_override or "").strip():
            raise HTTPException(status_code=400, detail="Please provide a schematic title before generating.")

        carrier_merges = _build_carrier_merges(validation_flags, req.warning_answers)
        result = run_pipeline(
            session.file_path,
            confirmed_warnings=True,
            account_name_override=(req.account_name_override or "").strip() or None,
            carrier_merges=carrier_merges or None,
        )

        if result["status"] != "ok":
            raise HTTPException(status_code=400, detail=result["report"])

        pptx_bytes = result["pptx_bytes"]
        download_name = os.path.splitext(session.file_name)[0] + "-schematic.pptx"
        return StreamingResponse(
            io.BytesIO(pptx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
        )
    finally:
        if os.path.exists(session.file_path):
            os.remove(session.file_path)


dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))

if os.path.exists(dist_path):
    assets_path = os.path.join(dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        return FileResponse(os.path.join(dist_path, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
