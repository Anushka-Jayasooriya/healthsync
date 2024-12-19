import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Settings
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    MONGO_DB = os.getenv('MONGO_DB_NAME', 'healthsync')

    # Redshift Settings
    REDSHIFT_DB = os.getenv('REDSHIFT_DB', 'healthsync')
    REDSHIFT_HOST = os.getenv('REDSHIFT_HOST')
    REDSHIFT_PORT = int(os.getenv('REDSHIFT_PORT', '5439'))
    REDSHIFT_USER = os.getenv('REDSHIFT_USER')
    REDSHIFT_PASSWORD = os.getenv('REDSHIFT_PASSWORD')