from fastapi import APIRouter, Depends

from app.core.deps import require_admin
from app.services.store import STORE

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("")
def get_audit_logs(
    page: int = 1,
    size: int = 30,
    action: str = "",
    entity_type: str = "",
    username: str = "",
    date_from: str = "",
    date_to: str = "",
    _: dict = Depends(require_admin),
) -> dict:
    return STORE.list_audit_logs(
        page=page,
        size=size,
        action=action,
        entity_type=entity_type,
        username=username,
        date_from=date_from,
        date_to=date_to,
    )
