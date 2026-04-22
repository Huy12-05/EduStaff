from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.services.store import STORE

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/overview")
def overview(_: dict = Depends(get_current_user)) -> dict:
    return STORE.overview_stats()


@router.get("/by-department")
def by_department(_: dict = Depends(get_current_user)) -> list[dict]:
    return STORE.stats_by_department()


@router.get("/by-degree")
def by_degree(_: dict = Depends(get_current_user)) -> list[dict]:
    return STORE.stats_by_degree()


@router.get("/by-position")
def by_position(_: dict = Depends(get_current_user)) -> list[dict]:
    return STORE.stats_by_position()


@router.get("/lecturer-status")
def lecturer_status(_: dict = Depends(get_current_user)) -> dict:
    return STORE.lecturer_status_stats()
