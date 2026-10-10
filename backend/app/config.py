from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./careeriq.db"
    jwt_secret: str = "development-only-change-this-secret-before-deployment"
    access_token_minutes: int = 60
    max_upload_mb: int = 10
    upload_dir: Path = Path("uploads")
    frontend_origins: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
