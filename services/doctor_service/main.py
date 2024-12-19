import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as doctor_router
from app.database import Database

app = FastAPI(
    title="Doctor Service API",
    description="API for managing doctor records in a healthcare system",
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
app.include_router(doctor_router, prefix="/doctors", tags=["doctors"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)