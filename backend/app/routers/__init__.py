from fastapi import APIRouter

from app.routers.account_router import router as account_router
from app.routers.audit_router import router as audit_router
from app.routers.auth_router import router as auth_router
from app.routers.backup_router import router as backup_router
from app.routers.department_router import router as department_router
from app.routers.lecturer_router import router as lecturer_router
from app.routers.schedule_router import router as schedule_router
from app.routers.stats_router import router as stats_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(department_router)
api_router.include_router(lecturer_router)
api_router.include_router(schedule_router)
api_router.include_router(account_router)
api_router.include_router(stats_router)
api_router.include_router(audit_router)
api_router.include_router(backup_router)
