from pydantic import BaseModel

class Settings(BaseModel):
    """
    Application configuration settings.
    """
    PROJECT_NAME: str = "Container Tracking API"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    TRACKING_SCRIPTS_DIR: str = "tracking_scripts"

    class Config:
        env_file = ".env"  # Load variables from .env file

# Global settings instance
settings = Settings()
