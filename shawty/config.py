from pydantic import BaseSettings


class Secrets(BaseSettings):
    DATABASE_URL: str
    API_KEY: str

    class Config:
        env_file = ".env"


secrets = Secrets()
