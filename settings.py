from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str
    DEBUG: bool

    # Пути
    BASE_DIR: Path
    UPLOAD_DIR: Path

    # Настройки базы данных
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"
        extra = "forbid"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Преобразуем BASE_DIR и UPLOAD_DIR в Path объекты
        self.BASE_DIR = Path(self.BASE_DIR).resolve()
        self.UPLOAD_DIR = self.BASE_DIR / self.UPLOAD_DIR
        
# Создаем объект настроек
settings = Settings()

