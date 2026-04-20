from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    lecturer_id: int
    subject_name: str
    subject_code: str
    room: str
    day_of_week: str
    start_time: str
    end_time: str
    semester: str
    academic_year: str


class ScheduleUpdate(BaseModel):
    lecturer_id: int | None = None
    subject_name: str | None = None
    subject_code: str | None = None
    room: str | None = None
    day_of_week: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    semester: str | None = None
    academic_year: str | None = None
