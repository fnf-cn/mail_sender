from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql://fnfadmin:fnfadmin123@172.16.72.73:5433/mail_sender"

    # SMTP 配置
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Mail Sender"

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # FastAPI 配置
    api_host: str = "0.0.0.0"
    api_port: int = 10001
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
