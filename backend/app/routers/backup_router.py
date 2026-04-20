import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.deps import require_admin
from app.services.store import STORE

router = APIRouter(prefix="/backup", tags=["Backup"])


def _backup_dir() -> Path:
    path = Path(settings.backup_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.get("/create")
def create_backup(_: dict = Depends(require_admin)) -> StreamingResponse:
    # Tao file JSON de mo phong backup trong giai doan skeleton.
    snapshot = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "overview": STORE.overview_stats(),
    }
    raw = json.dumps(snapshot, ensure_ascii=False, indent=2).encode("utf-8")
    return StreamingResponse(
        iter([raw]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": 'attachment; filename="backup.json"'},
    )


@router.get("/list")
def list_backups(_: dict = Depends(require_admin)) -> list[dict]:
    folder = _backup_dir()
    files = []
    for fp in sorted(folder.glob("*"), reverse=True):
        if not fp.is_file():
            continue
        files.append(
            {
                "filename": fp.name,
                "size_bytes": fp.stat().st_size,
                "created_at": datetime.fromtimestamp(fp.stat().st_mtime).isoformat(timespec="seconds"),
            }
        )
    return files


@router.post("/restore")
def restore_backup(filename: str = Form(...), _: dict = Depends(require_admin)) -> dict[str, str]:
    folder = _backup_dir()
    target = folder / filename
    if not target.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay file backup.")
    return {"message": "Restore thanh cong (placeholder)."}


@router.delete("/{filename}")
def delete_backup(filename: str, _: dict = Depends(require_admin)) -> dict[str, str]:
    folder = _backup_dir()
    target = folder / filename
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay file backup.")
    os.remove(target)
    return {"message": "Xoa backup thanh cong."}
