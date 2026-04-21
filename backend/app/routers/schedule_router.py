from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import get_current_user, require_admin
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.services.audit_service import log_action
from app.services.store import STORE

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.get("/week/detail")
def get_week_slot_detail(
    start_time: str = Query(..., description="HH:MM"),
    end_time: str = Query(..., description="HH:MM"),
    semester: str = "",
    academic_year: str = "",
    _: dict = Depends(get_current_user),
) -> dict:
    items = STORE.get_slot_detail(
        start_time=start_time,
        end_time=end_time,
        semester=semester,
        academic_year=academic_year,
    )
    return {"items": items, "total": len(items)}


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lịch giảng dạy.")
    return row


@router.post("")
def create_schedule(payload: ScheduleCreate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.create_schedule(payload.model_dump())
    log_action("create", "schedule", admin["username"], f"Tạo lịch dạy {row['id']}", row["id"])
    return row


@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, payload: ScheduleUpdate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.update_schedule(schedule_id, payload.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lịch giảng dạy.")
    log_action("update", "schedule", admin["username"], f"Cập nhật lịch dạy {schedule_id}", schedule_id)
    return row


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, admin: dict = Depends(require_admin)) -> dict[str, str]:
    ok = STORE.delete_schedule(schedule_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy lịch giảng dạy.")
    log_action("delete", "schedule", admin["username"], f"Xóa lịch dạy {schedule_id}", schedule_id)
    return {"message": "Xóa lịch giảng dạy thành công."}
