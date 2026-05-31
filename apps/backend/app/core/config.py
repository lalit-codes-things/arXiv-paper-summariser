import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Arxiv Research Copilot"
    api_version: str = "v1"
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 12


settings = Settings()
