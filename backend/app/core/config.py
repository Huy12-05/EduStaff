from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduStaff Backend"
    app_env: str = "dev"
    debug: bool = True

    database_url: str = "mysql+pymysql://edustaff:edustaff_password@localhost:3306/edustaff"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    backup_dir: str = "./backups"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def _validate_jwt_secret(self) -> "Settings":
        if self.app_env == "production" and self.jwt_secret_key == "change-me":
            raise ValueError(
                "JWT_SECRET_KEY must be set to a strong random value in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return self


settings = Settings()
