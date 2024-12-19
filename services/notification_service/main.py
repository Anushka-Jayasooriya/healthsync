import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import router as notification_router
from app.database import Database

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Notification Service API",
    description="API for sending and managing notifications",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to database
Database.connect()

# Include routers
app.include_router(notification_router, prefix="/notifications", tags=["notifications"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8005, reload=True)