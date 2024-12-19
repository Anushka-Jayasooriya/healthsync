from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as appointment_router
from app.database import Database

app = FastAPI(
    title="Appointment Service API",
    description="API for managing medical appointments",
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
app.include_router(appointment_router, prefix="/appointments", tags=["appointments"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)