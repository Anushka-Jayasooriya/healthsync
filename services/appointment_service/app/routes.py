from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
from typing import List, Optional
from datetime import datetime, date
from bson import ObjectId
from .models import Appointment, AppointmentStatus
from .database import Database
from .services import get_patient_details, get_doctor_details, send_appointment_notification

router = APIRouter()
appointments_collection = Database.get_collection("appointments")

def validate_object_id(object_id: str):
    try:
        return ObjectId(object_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@router.post("/", response_model=dict)
async def schedule_appointment(
        appointment: Appointment,
        background_tasks: BackgroundTasks
):
    """Schedule a new appointment"""
    # Validate patient and doctor
    patient = await get_patient_details(appointment.patient_id)
    doctor = await get_doctor_details(appointment.doctor_id)

    # Insert appointment
    appointment_dict = appointment.dict()
    result = appointments_collection.insert_one(appointment_dict)

    # Send notification
    background_tasks.add_task(
        send_appointment_notification,
        patient.get("email", ""),
        doctor.get("name", ""),
        str(appointment.appointment_date),
        appointment.appointment_time
    )

    return {"id": str(result.inserted_id), "message": "Appointment scheduled successfully"}

@router.get("/{appointment_id}", response_model=dict)
async def get_appointment(appointment_id: str = Path(..., title="The ID of the appointment")):
    """Get appointment details"""
    appointment = appointments_collection.find_one({"_id": validate_object_id(appointment_id)})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Get related details
    patient = await get_patient_details(appointment["patient_id"])
    doctor = await get_doctor_details(appointment["doctor_id"])

    appointment["id"] = str(appointment.pop("_id"))
    appointment["patient_details"] = patient
    appointment["doctor_details"] = doctor

    return appointment

@router.get("/", response_model=List[dict])
async def list_appointments(
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None,
        status: Optional[AppointmentStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100)
):
    """List appointments with filters"""
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if doctor_id:
        query["doctor_id"] = doctor_id
    if status:
        query["status"] = status
    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = date_from.isoformat()
        if date_to:
            date_query["$lte"] = date_to.isoformat()
        if date_query:
            query["appointment_date"] = date_query

    appointments = list(appointments_collection.find(query).skip(skip).limit(limit))
    return [{"id": str(app.pop("_id")), **app} for app in appointments]

@router.put("/{appointment_id}/status", response_model=dict)
async def update_appointment_status(
        appointment_id: str,
        status: AppointmentStatus,
        background_tasks: BackgroundTasks
):
    """Update appointment status"""
    result = appointments_collection.update_one(
        {"_id": validate_object_id(appointment_id)},
        {
            "$set": {
                "status": status,
                "updated_at": datetime.now()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return {"message": f"Appointment status updated to {status}"}