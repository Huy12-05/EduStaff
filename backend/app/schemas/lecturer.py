from pydantic import BaseModel


class LecturerCreate(BaseModel):
    employee_code: str
    full_name: str
    email: str
    phone: str | None = None
    gender: str = "male"
    date_of_birth: str | None = None
    degree: str
    position: str | None = None
    department_id: int
    hire_date: str | None = None
    status: str = "active"


class LecturerUpdate(BaseModel):
    employee_code: str | None = None
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    degree: str | None = None
    position: str | None = None
    department_id: int | None = None
    hire_date: str | None = None
    status: str | None = None
