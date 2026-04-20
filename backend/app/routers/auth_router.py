from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.schemas.auth import ChangePasswordRequest, CurrentUserResponse, TokenResponse
from app.services.audit_service import log_action
from app.services.store import STORE

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = STORE.find_account_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sai username hoac password.")
    if not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tai khoan da bi khoa.")

    access_token = create_access_token({"sub": user["username"], "role": user["role"]})
    log_action("login", "account", user["username"], "Dang nhap he thong", user["id"])
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=CurrentUserResponse)
def get_me(user: dict = Depends(get_current_user)) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "is_active": user["is_active"],
    }


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, user: dict = Depends(get_current_user)) -> dict[str, str]:
    if not verify_password(payload.old_password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mat khau cu khong dung.")
    STORE.change_password(user["username"], payload.new_password)
    log_action("update", "account", user["username"], "Doi mat khau", user["id"])
    return {"message": "Doi mat khau thanh cong."}
