from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=4)
    new_password: str = Field(min_length=6)


class CurrentUserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool
