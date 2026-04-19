from datetime import datetime

from app.services.store import STORE


def log_action(action: str, entity_type: str, username: str, details: str, entity_id: int | None = None) -> None:
    STORE.add_audit_log(
        {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
            "username": username,
            "ip_address": "127.0.0.1",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
