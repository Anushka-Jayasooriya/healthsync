import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PATIENT_SERVICE_URL = os.getenv("PATIENT_SERVICE_URL", "http://34.71.102.253:8001")
    DOCTOR_SERVICE_URL = os.getenv("DOCTOR_SERVICE_URL", "http://34.44.196.226:8002")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://34.134.196.5:8005")

settings = Settings()
