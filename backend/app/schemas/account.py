from pydantic import BaseModel


class AccountCreate(BaseModel):
    username: str
    full_name: str
    role: str = "staff"
    password: str


class AccountUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    password: str | None = None


class ResetPasswordRequest(BaseModel):
    new_password: str
