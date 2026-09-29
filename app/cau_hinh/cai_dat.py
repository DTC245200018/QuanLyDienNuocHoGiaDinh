"""
Doc cau hinh tu file .env.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class CaiDat(BaseSettings):
    """Cac thiet lap he thong."""

    db_server: str = "localhost"
    db_database: str = "QuanLyDienNuoc"
    db_driver: str = "ODBC Driver 17 for SQL Server"

    # AI — mac dinh Groq
    ai_provider: str = "groq"
    ai_api_key: str = ""
    ai_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    ai_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


cai_dat = CaiDat()