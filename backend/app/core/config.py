import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "SatQuery AI API"
    
    # Base directory (backend folder)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # Upload limits and allowed formats
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    ALLOWED_IMAGE_CONTENT_TYPES: set = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
    
    # MongoDB Config
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "satquery_db")

    # JWT Authentication Config
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_if_not_set_in_env")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

settings = Settings()
