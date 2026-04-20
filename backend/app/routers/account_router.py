from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import require_admin
from app.schemas.account import AccountCreate, AccountUpdate, ResetPasswordRequest
from app.services.audit_service import log_action
from app.services.store import STORE

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("")
def list_accounts(search: str = "", role: str = "", is_active: bool | None = None, admin: dict = Depends(require_admin)) -> list[dict]:
    return STORE.list_accounts(search=search, role=role, is_active=is_active)


@router.get("/{account_id}")
def get_account(account_id: int, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.get_account(account_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai khoan.")
    return row


@router.post("")
def create_account(payload: AccountCreate, admin: dict = Depends(require_admin)) -> dict:
    if STORE.find_account_by_username(payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username da ton tai.")
    row = STORE.create_account(payload.model_dump())
    log_action("create", "account", admin["username"], f"Tao tai khoan {row['username']}", row["id"])
    return row


@router.put("/{account_id}")
def update_account(account_id: int, payload: AccountUpdate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.update_account(account_id, payload.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai khoan.")
    log_action("update", "account", admin["username"], f"Cap nhat tai khoan {account_id}", account_id)
    return row


@router.patch("/{account_id}/toggle-active")
def toggle_account(account_id: int, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.toggle_account(account_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai khoan.")
    action = "Khoa" if not row.get("is_active") else "Mo khoa"
    log_action("update", "account", admin["username"], f"{action} tai khoan {account_id}", account_id)
    return row


@router.post("/{account_id}/reset-password")
def reset_password(account_id: int, payload: ResetPasswordRequest, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.reset_password(account_id, payload.new_password)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai khoan.")
    log_action("update", "account", admin["username"], f"Reset password tai khoan {account_id}", account_id)
    return {"message": "Dat lai mat khau thanh cong."}


@router.delete("/{account_id}")
def delete_account(account_id: int, admin: dict = Depends(require_admin)) -> dict[str, str]:
    if account_id == admin["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Khong the xoa tai khoan dang dang nhap.")
    ok = STORE.delete_account(account_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay tai khoan.")
    log_action("delete", "account", admin["username"], f"Xoa tai khoan {account_id}", account_id)
    return {"message": "Xoa tai khoan thanh cong."}
