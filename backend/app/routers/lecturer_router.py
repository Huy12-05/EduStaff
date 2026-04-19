from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user, require_admin
from app.schemas.lecturer import LecturerCreate, LecturerUpdate
from app.services.audit_service import log_action
from app.services.store import STORE

router = APIRouter(prefix="/lecturers", tags=["Lecturers"])


@router.get("")
def list_lecturers(
    page: int = 1,
    size: int = 20,
    search: str = "",
    department_id: int | None = None,
    degree: str = "",
    position: str = "",
    gender: str = "",
    status_filter: str = Query("", alias="status"),
    _: dict = Depends(get_current_user),
) -> dict:
    return STORE.list_lecturers(
        page=page,
        size=size,
        search=search,
        department_id=department_id,
        degree=degree,
        position=position,
        gender=gender,
        status=status_filter,
    )


@router.post("")
def create_lecturer(payload: LecturerCreate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.create_lecturer(payload.model_dump())
    log_action("create", "lecturer", admin["username"], f"Tao giang vien {row['employee_code']}", row["id"])
    return row


@router.put("/{lecturer_id}")
def update_lecturer(lecturer_id: int, payload: LecturerUpdate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.update_lecturer(lecturer_id, payload.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay giang vien.")
    log_action("update", "lecturer", admin["username"], f"Cap nhat giang vien {lecturer_id}", lecturer_id)
    return row


@router.delete("/{lecturer_id}")
def delete_lecturer(lecturer_id: int, admin: dict = Depends(require_admin)) -> dict[str, str]:
    ok = STORE.delete_lecturer(lecturer_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay giang vien.")
    log_action("delete", "lecturer", admin["username"], f"Xoa giang vien {lecturer_id}", lecturer_id)
    return {"message": "Xoa giang vien thanh cong."}


@router.post("/{lecturer_id}/avatar")
def upload_avatar(lecturer_id: int, _: dict = Depends(require_admin)) -> dict[str, str]:
    # Placeholder de giu hop dong API voi frontend.
    if not STORE.get_lecturer(lecturer_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay giang vien.")
    return {"message": "Upload avatar thanh cong (placeholder)."}


@router.get("/export")
def export_lecturers_excel(
    search: str = "",
    department_id: int | None = None,
    degree: str = "",
    status_filter: str = Query("", alias="status"),
    _: dict = Depends(get_current_user),
) -> StreamingResponse:
    data = STORE.list_lecturers(
        page=1,
        size=10000,
        search=search,
        department_id=department_id,
        degree=degree,
        position="",
        gender="",
        status=status_filter,
    )

    lines = ["employee_code,full_name,email,department,degree,status"]
    for row in data["items"]:
        dep_name = (row.get("department") or {}).get("name", "")
        lines.append(
            f"{row.get('employee_code','')},{row.get('full_name','')},{row.get('email','')},{dep_name},{row.get('degree','')},{row.get('status','')}"
        )
    csv_bytes = "\n".join(lines).encode("utf-8")
    filename = f"lecturers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/pdf")
def export_lecturers_pdf(_: dict = Depends(get_current_user)) -> StreamingResponse:
    # Placeholder PDF bytes.
    content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF"
    filename = f"lecturers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{lecturer_id}")
def get_lecturer(lecturer_id: int, _: dict = Depends(get_current_user)) -> dict:
    row = STORE.get_lecturer(lecturer_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay giang vien.")
    return row
