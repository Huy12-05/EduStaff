from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user, require_admin
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.services.audit_service import log_action
from app.services.store import STORE

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.get("")
def list_schedules(
    page: int = 1,
    size: int = 20,
    lecturer_id: int | None = None,
    day_of_week: str = "",
    semester: str = "",
    academic_year: str = "",
    _: dict = Depends(get_current_user),
) -> dict:
    return STORE.list_schedules(
        page=page,
        size=size,
        lecturer_id=lecturer_id,
        day_of_week=day_of_week,
        semester=semester,
        academic_year=academic_year,
    )


@router.get("/{schedule_id}")
def get_schedule(schedule_id: int, _: dict = Depends(get_current_user)) -> dict:
    row = STORE.get_schedule(schedule_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay lich giang day.")
    return row


@router.post("")
def create_schedule(payload: ScheduleCreate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.create_schedule(payload.model_dump())
    log_action("create", "schedule", admin["username"], f"Tao lich day {row['id']}", row["id"])
    return row


@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, payload: ScheduleUpdate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.update_schedule(schedule_id, payload.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay lich giang day.")
    log_action("update", "schedule", admin["username"], f"Cap nhat lich day {schedule_id}", schedule_id)
    return row


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, admin: dict = Depends(require_admin)) -> dict[str, str]:
    ok = STORE.delete_schedule(schedule_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay lich giang day.")
    log_action("delete", "schedule", admin["username"], f"Xoa lich day {schedule_id}", schedule_id)
    return {"message": "Xoa lich giang day thanh cong."}
