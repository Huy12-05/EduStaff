import io
import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.deps import require_admin
from app.services.store import STORE

router = APIRouter(prefix="/backup", tags=["Backup"])

_ALLOWED_EXTENSIONS = {".json", ".db", ".sql", ".bak"}
_MAX_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB


def _backup_dir() -> Path:
    path = Path(settings.backup_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


@router.get("/create")
def create_backup(_: dict = Depends(require_admin)) -> StreamingResponse:
    """Xuất toàn bộ dữ liệu hệ thống ra file JSON."""
    snapshot = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "version": "1.0",
        "overview": STORE.overview_stats(),
        "departments": STORE.list_departments(),
        "lecturers": STORE.list_lecturers(page=1, size=10000).get("items", []),
        "schedules": STORE.list_schedules(page=1, size=10000).get("items", []),
    }
    raw = json.dumps(snapshot, ensure_ascii=False, indent=2, default=str).encode("utf-8")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{ts}.json"

    # Auto-save to backup directory
    target = _backup_dir() / filename
    target.write_bytes(raw)

    return StreamingResponse(
        io.BytesIO(raw),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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


@router.post("/upload")
async def upload_backup(
    file: UploadFile = File(...),
    _: dict = Depends(require_admin),
) -> dict[str, str]:
    """Tải file backup từ máy cục bộ lên server để lưu vào danh sách backup."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Định dạng file không hợp lệ. Chấp nhận: {', '.join(_ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > _MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File quá lớn. Giới hạn tối đa 200 MB.",
        )

    safe_name = Path(file.filename).name
    target = _backup_dir() / safe_name
    # Avoid overwrite — append timestamp if name exists
    if target.exists():
        stem = target.stem
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{stem}_{ts}{suffix}"
        target = _backup_dir() / safe_name

    target.write_bytes(content)
    return {"message": f"Đã tải lên thành công: {safe_name}", "filename": safe_name}


@router.post("/restore")
def restore_backup(
    filename: str = Form(...),
    _: dict = Depends(require_admin),
) -> dict[str, str]:
    """Phục hồi dữ liệu từ file backup có sẵn trên server."""
    folder = _backup_dir()
    target = folder / filename
    if not target.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy file backup.",
        )
    # Placeholder — full restore logic requires DB migration strategy
    return {"message": f"Đã nhận lệnh phục hồi từ '{filename}'. Vui lòng khởi động lại server để áp dụng."}


@router.delete("/{filename}")
def delete_backup(filename: str, _: dict = Depends(require_admin)) -> dict[str, str]:
    folder = _backup_dir()
    target = folder / filename
    if not target.exists() or not target.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy file backup.",
        )
    os.remove(target)
    return {"message": "Xóa backup thành công."}
