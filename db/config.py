from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://root:root@pg_db:5432/my_db"

settings = Settings()
