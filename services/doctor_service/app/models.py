from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import List, Optional
from datetime import datetime, date

class Schedule(BaseModel):
    date: date
    start_time: str
    end_time: str
    is_available: bool = True

    # Convert date to ISO format string for MongoDB
    @field_serializer('date')
    def serialize_date(self, dt: date) -> str:
        return dt.isoformat()

class Qualification(BaseModel):
    degree: str
    institution: str
    year: int

class Doctor(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    specialty: str
    qualifications: List[Qualification] = []
    schedule: List[Schedule] = []
    email: EmailStr
    phone: Optional[str] = None
    experience_years: Optional[int] = Field(None, ge=0)
    consultation_fee: Optional[float] = Field(None, ge=0)
    languages: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)