from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, date
from app.models import Doctor, Schedule, Qualification
from app.database import Database

router = APIRouter()
doctors_collection = Database.get_collection("doctors")

def validate_object_id(object_id: str):
    try:
        return ObjectId(object_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@router.post("/", response_model=dict)
async def add_doctor(doctor: Doctor):
    """Create a new doctor record"""
    doctor_dict = doctor.dict()
    result = doctors_collection.insert_one(doctor_dict)
    return {"id": str(result.inserted_id), "message": "Doctor created successfully"}

@router.get("/{doctor_id}", response_model=dict)
async def get_doctor(doctor_id: str):
    """Retrieve a doctor record by ID"""
    doctor = doctors_collection.find_one({"_id": validate_object_id(doctor_id)})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor["id"] = str(doctor.pop("_id"))
    return doctor

@router.get("/", response_model=List[dict])
async def list_doctors(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        specialty: Optional[str] = None,
        language: Optional[str] = None
):
    """List all doctors with pagination and optional filters"""
    query = {}
    if specialty:
        query["specialty"] = {"$regex": specialty, "$options": "i"}
    if language:
        query["languages"] = {"$in": [language]}

    doctors = list(doctors_collection.find(query).skip(skip).limit(limit))
    return [{**doctor, "id": str(doctor.pop("_id"))} for doctor in doctors]

@router.put("/{doctor_id}", response_model=dict)
async def update_doctor(doctor_id: str, doctor: Doctor):
    """Update a doctor record"""
    doctor_dict = doctor.dict()
    doctor_dict["updated_at"] = datetime.now()

    result = doctors_collection.update_one(
        {"_id": validate_object_id(doctor_id)},
        {"$set": doctor_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return {"message": "Doctor updated successfully"}

@router.delete("/{doctor_id}", response_model=dict)
async def delete_doctor(doctor_id: str):
    """Delete a doctor record"""
    result = doctors_collection.delete_one({"_id": validate_object_id(doctor_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return {"message": "Doctor deleted successfully"}

@router.post("/{doctor_id}/schedule", response_model=dict)
async def add_schedule(doctor_id: str, schedule: Schedule):
    """Add a schedule slot for a doctor"""
    result = doctors_collection.update_one(
        {"_id": validate_object_id(doctor_id)},
        {
            "$push": {"schedule": schedule.dict()},
            "$set": {"updated_at": datetime.now()}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return {"message": "Schedule added successfully"}

@router.get("/{doctor_id}/available-slots", response_model=List[Schedule])
async def get_available_slots(
        doctor_id: str,
        date: Optional[date] = None
):
    """Get available slots for a doctor"""
    query = {"_id": validate_object_id(doctor_id)}
    if date:
        query["schedule.date"] = date

    doctor = doctors_collection.find_one(query)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    available_slots = [
        Schedule(**slot)
        for slot in doctor.get("schedule", [])
        if slot.get("is_available") and (not date or slot["date"] == date)
    ]

    return available_slots