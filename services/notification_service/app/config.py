from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # MongoDB Settings
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb+srv://Anushka:e1daUI2XWSFovIYl@cluster0.u44yf.mongodb.net")
    DB_NAME: str = os.getenv("DB_NAME", "healthsync")

    # SMTP Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "niroshaama74@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "uchx jywq wyzo vwgn")

    # Email Settings
    DEFAULT_FROM_EMAIL: str = SMTP_USERNAME
    EMAIL_TEMPLATES_DIR: str = "app/templates"

settings = Settings()
