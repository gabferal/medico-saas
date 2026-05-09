from pydantic_settings import BaseSettings, SettingsConfigDict # Importación actualizada
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    admin_email: str
    admin_password: str
    environment: str = "development"

    # Cambiamos 'class Config' por 'model_config' (Estándar de Pydantic V2)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

@lru_cache()
def get_settings() -> Settings:
    return Settings()