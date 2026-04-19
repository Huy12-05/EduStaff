from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import get_current_user, require_admin
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.services.audit_service import log_action
from app.services.store import STORE

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("")
def list_departments(
    page: str = Query("1"),
    size: str = Query("50"),
    search: str = "",
    _: dict = Depends(get_current_user),
) -> list[dict]:
    # Ho tro frontend hien tai goi sai tham so (search truyen vao page).
    if not search and page and not str(page).isdigit():
        search = str(page)
    return STORE.list_departments(search=search)


@router.get("/{department_id}")
def get_department(department_id: int, _: dict = Depends(get_current_user)) -> dict:
    row = STORE.get_department(department_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa.")
    return row


@router.post("")
def create_department(payload: DepartmentCreate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.create_department(payload.model_dump())
    log_action("create", "department", admin["username"], f"Tao khoa {row['name']}", row["id"])
    return row


@router.put("/{department_id}")
def update_department(department_id: int, payload: DepartmentUpdate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.update_department(department_id, payload.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa.")
    log_action("update", "department", admin["username"], f"Cap nhat khoa {department_id}", department_id)
    return row


@router.delete("/{department_id}")
def delete_department(department_id: int, admin: dict = Depends(require_admin)) -> dict[str, str]:
    try:
        ok = STORE.delete_department(department_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khoa.")
    log_action("delete", "department", admin["username"], f"Xoa khoa {department_id}", department_id)
    return {"message": "Xoa khoa thanh cong."}
