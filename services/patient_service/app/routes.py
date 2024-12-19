from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.models import Patient, MedicalRecord
from app.database import Database

router = APIRouter()
patients_collection = Database.get_collection("patients")

def validate_object_id(object_id: str):
    try:
        return ObjectId(object_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@router.post("/", response_model=dict)
async def add_patient(patient: Patient):
    """Create a new patient record"""
    patient_dict = patient.dict()
    result = patients_collection.insert_one(patient_dict)
    return {"id": str(result.inserted_id), "message": "Patient created successfully"}

@router.get("/{patient_id}", response_model=dict)
async def get_patient(patient_id: str):
    """Retrieve a patient record by ID"""
    patient = patients_collection.find_one({"_id": validate_object_id(patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient["id"] = str(patient.pop("_id"))
    return patient

@router.put("/{patient_id}", response_model=dict)
async def update_patient(patient_id: str, patient: Patient):
    """Update a patient record"""
    patient_dict = patient.dict()
    patient_dict["updated_at"] = datetime.now()

    result = patients_collection.update_one(
        {"_id": validate_object_id(patient_id)},
        {"$set": patient_dict}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Patient updated successfully"}

@router.delete("/{patient_id}", response_model=dict)
async def delete_patient(patient_id: str):
    """Delete a patient record"""
    result = patients_collection.delete_one({"_id": validate_object_id(patient_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Patient deleted successfully"}

@router.post("/{patient_id}/medical-records", response_model=dict)
async def add_medical_record(patient_id: str, record: MedicalRecord):
    """Add a medical record to a patient's history"""
    result = patients_collection.update_one(
        {"_id": validate_object_id(patient_id)},
        {
            "$push": {"medical_history": record.dict()},
            "$set": {"updated_at": datetime.now()}
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {"message": "Medical record added successfully"}