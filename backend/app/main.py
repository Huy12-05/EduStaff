from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db
from app.routers import api_router
from app.services.store import STORE


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Backend API skeleton cho he thong EduStaff.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.on_event("startup")
    def on_startup() -> None:
        # Khoi tao bang DB va du lieu mac dinh cho lan chay dau.
        init_db()
        STORE.seed_initial_data()

    @app.get("/health", tags=["System"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
