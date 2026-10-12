import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Indonesian KTP OCR & Age Validation API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1")
    
    # OCR settings
    OCR_LANGUAGES: list[str] = ["id", "en"]
    OCR_USE_GPU: bool = os.getenv("OCR_USE_GPU", "False").lower() in ("true", "1")
    
    # Age Validation Settings
    MINIMUM_AGE_REQUIRED: int = int(os.getenv("MINIMUM_AGE_REQUIRED", "18"))
    
    # Image constraints
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "15"))
    MAX_IMAGE_DIMENSION: int = 1800  # Resize if larger for OCR performance & speed

settings = Settings()
