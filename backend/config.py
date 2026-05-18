from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/"
    MONGO_DB: str = "safescan"
    JWT_SECRET: str = "change-this-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    GEMINI_API_KEY: str = ""
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"

settings = Settings()