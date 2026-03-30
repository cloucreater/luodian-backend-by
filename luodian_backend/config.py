from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = 'your_secret_key'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = 'sqlite:///./database.sqlite'

    AI_PROVIDER: str = 'openai'
    OPENAI_API_KEY: str = ''
    OPENAI_BASE_URL: str = 'https://api.openai.com/v1'
    ZHIPU_API_KEY: str = ''
    LOCAL_MODEL_URL: str = 'http://localhost:8000/generate'

    class Config:
        env_file = '.env'

settings = Settings()
