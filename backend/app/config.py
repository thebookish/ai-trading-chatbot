from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    ALLOW_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    DATA_PROVIDER: str = "openai"  # or "mock"
    OPENAI_API_KEY: str ='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'
    MODEL_NAME: str = "gpt-4o-mini"

settings = Settings()
