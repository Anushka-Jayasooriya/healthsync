from fastapi import HTTPException
import httpx
from datetime import datetime
from .config import settings

async def get_patient_details(patient_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.PATIENT_SERVICE_URL}/patients/{patient_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=404, detail=f"Patient not found: {str(e)}")

async def get_doctor_details(doctor_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.DOCTOR_SERVICE_URL}/doctors/{doctor_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=404, detail=f"Doctor not found: {str(e)}")

async def send_appointment_notification(
        patient_email: str,
        doctor_name: str,
        appointment_date: str,
        appointment_time: str
):
    notification_data = {
        "recipient_email": patient_email,
        "subject": f"Appointment Scheduled with {doctor_name}",
        "content": f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto;">
                    <h2 style="color: #2c3e50;">Appointment Confirmation</h2>
                    
                    <p>Your appointment has been confirmed with the following details:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Doctor:</strong> {doctor_name}</p>
                        <p><strong>Date:</strong> {appointment_date}</p>
                        <p><strong>Time:</strong> {appointment_time}</p>
                    </div>

                    <h3 style="color: #34495e;">Important Reminders:</h3>
                    <ul>
                        <li>Please arrive 15 minutes before your appointment time</li>
                        <li>Bring any relevant medical records or test results</li>
                        <li>Bring a list of current medications</li>
                        <li>Don't forget to wear a mask</li>
                    </ul>

                    <p style="color: #7f8c8d;">If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
                    
                    <p style="margin-top: 30px;">Best regards,<br>HealthSync Medical Center</p>

                    <div style="margin-top: 30px; font-size: 12px; color: #95a5a6;">
                        <p>This is an automated message, please do not reply to this email.</p>
                        <p>For any queries, please contact our help desk: support@healthsync.com</p>
                    </div>
                </div>
            </body>
        </html>
        """.strip(),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/notifications/send",
                json=notification_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to send notification: {str(e)}")
            return None