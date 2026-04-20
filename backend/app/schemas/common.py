from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    message: str


class PaginationResponse(BaseModel):
    items: list[dict] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    size: int = 20
    pages: int = 1
