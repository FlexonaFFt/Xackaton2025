from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Application"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

settings = Settings()