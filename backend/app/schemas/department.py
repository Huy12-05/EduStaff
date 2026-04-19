from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    code: str
    name: str
    description: str | None = None


class DepartmentUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    description: str | None = None
