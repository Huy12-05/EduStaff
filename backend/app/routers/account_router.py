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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản.")
    return row


@router.post("")
def create_account(payload: AccountCreate, admin: dict = Depends(require_admin)) -> dict:
    if STORE.find_account_by_username(payload.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username đã tồn tại.")
    row = STORE.create_account(payload.model_dump())
    log_action("create", "account", admin["username"], f"Tạo tài khoản {row['username']}", row["id"])
    return row


@router.put("/{account_id}")
def update_account(account_id: int, payload: AccountUpdate, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.update_account(account_id, payload.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản.")
    log_action("update", "account", admin["username"], f"Cập nhật tài khoản {account_id}", account_id)
    return row


@router.patch("/{account_id}/toggle-active")
def toggle_account(account_id: int, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.toggle_account(account_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản.")
    action = "Khóa" if not row.get("is_active") else "Mở khóa"
    log_action("update", "account", admin["username"], f"{action} tài khoản {account_id}", account_id)
    return row


@router.post("/{account_id}/reset-password")
def reset_password(account_id: int, payload: ResetPasswordRequest, admin: dict = Depends(require_admin)) -> dict:
    row = STORE.reset_password(account_id, payload.new_password)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản.")
    log_action("update", "account", admin["username"], f"Đặt lại mật khẩu tài khoản {account_id}", account_id)
    return {"message": "Đặt lại mật khẩu thành công."}


@router.delete("/{account_id}")
def delete_account(account_id: int, admin: dict = Depends(require_admin)) -> dict[str, str]:
    if account_id == admin["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể xóa tài khoản đang đăng nhập.")
    ok = STORE.delete_account(account_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài khoản.")
    log_action("delete", "account", admin["username"], f"Xóa tài khoản {account_id}", account_id)
    return {"message": "Xóa tài khoản thành công."}
