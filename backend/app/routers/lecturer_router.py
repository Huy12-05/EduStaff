from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

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
    try:
        row = STORE.create_lecturer(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    log_action("create", "lecturer", admin["username"], f"Tao giang vien {row['employee_code']}", row["id"])
    return row


@router.put("/{lecturer_id}")
def update_lecturer(lecturer_id: int, payload: LecturerUpdate, admin: dict = Depends(require_admin)) -> dict:
    try:
        row = STORE.update_lecturer(lecturer_id, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
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
    position: str = "",
    gender: str = "",
    status_filter: str = Query("", alias="status"),
    _: dict = Depends(get_current_user),
) -> StreamingResponse:
    data = STORE.list_lecturers(
        page=1, size=10000,
        search=search, department_id=department_id,
        degree=degree, position=position,
        gender=gender, status=status_filter,
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách giảng viên"

    headers = ["Mã GV", "Họ và tên", "Email", "SĐT", "Giới tính",
               "Ngày sinh", "Học vị", "Chức vụ", "Khoa/Bộ môn",
               "Ngày vào làm", "Trạng thái"]
    header_fill = PatternFill("solid", fgColor="1F6FEB")
    header_font = Font(bold=True, color="FFFFFF")
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    STATUS_MAP = {"active": "Đang dạy", "inactive": "Nghỉ việc", "on_leave": "Nghỉ phép"}
    GENDER_MAP = {"male": "Nam", "female": "Nữ", "other": "Khác"}
    for r_idx, row in enumerate(data["items"], 2):
        dep_name = (row.get("department") or {}).get("name", "")
        ws.append([
            row.get("employee_code", ""),
            row.get("full_name", ""),
            row.get("email", ""),
            row.get("phone", "") or "",
            GENDER_MAP.get(row.get("gender", ""), row.get("gender", "")),
            row.get("date_of_birth", "") or "",
            row.get("degree", ""),
            row.get("position", "") or "",
            dep_name,
            row.get("hire_date", "") or "",
            STATUS_MAP.get(row.get("status", ""), row.get("status", "")),
        ])

    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=8)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"lecturers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        buf,
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
