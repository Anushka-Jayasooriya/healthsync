from pydantic import BaseModel, Field, EmailStr, field_serializer
from typing import List, Optional
from datetime import datetime, date
from enum import Enum

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_date: date
    appointment_time: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    symptoms: List[str]
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Serialize date to string for MongoDB
    @field_serializer('appointment_date')
    def serialize_date(self, dt: date) -> str:
        return dt.isoformat()

    # Serialize datetime to string for MongoDB
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }