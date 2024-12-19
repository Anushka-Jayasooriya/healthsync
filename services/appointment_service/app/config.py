import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://127.0.0.1:8001")
    DOCTOR_SERVICE_URL = os.getenv("DOCTOR_SERVICE_URL", "http://127.0.0.1:8002")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://127.0.0.1:8005")

settings = Settings()
