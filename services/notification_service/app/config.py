from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # MongoDB Settings
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb+srv://eshan:yprexsHcK7ejG2yY@atlascluster.sqtnfv7.mongodb.net")
    DB_NAME: str = os.getenv("DB_NAME", "healthsync")

    # SMTP Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "shehan.krishan.dev@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "obek qfqv wual htjo")

    # Email Settings
    DEFAULT_FROM_EMAIL: str = SMTP_USERNAME
    EMAIL_TEMPLATES_DIR: str = "app/templates"

settings = Settings()