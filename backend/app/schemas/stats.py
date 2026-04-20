from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_lecturers: int
    total_departments: int
    total_schedules: int
    total_accounts: int
