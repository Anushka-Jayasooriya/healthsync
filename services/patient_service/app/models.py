from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class MedicalRecord(BaseModel):
    condition: str
    diagnosis_date: datetime
    notes: Optional[str] = None

class Patient(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., gt=0, lt=150)
    gender: str = Field(..., pattern="^(male|female|other)$")
    email: EmailStr
    medical_history: List[MedicalRecord] = []
    contact_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)