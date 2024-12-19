# app/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging
from datetime import datetime
from bson import ObjectId  # Add this import
from .models import Notification, NotificationStatus
from .database import Database
from .email_sender import send_email

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
notification_collection = Database.get_collection("notifications")

@router.post("/send", response_model=dict)
async def send_notification(notification: Notification, background_tasks: BackgroundTasks):
    """Send a new notification"""
    try:
        logger.info(f"Creating notification for: {notification.recipient_email}")

        # Save notification to database
        notification_dict = notification.dict()
        result = notification_collection.insert_one(notification_dict)
        notification_id = str(result.inserted_id)

        logger.info(f"Notification created with ID: {notification_id}")
        logger.info(f"Adding to background tasks queue...")

        # Send email in background
        background_tasks.add_task(process_notification, notification_id)

        return {
            "message": "Notification queued successfully",
            "id": notification_id
        }
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create notification: {str(e)}")

async def process_notification(notification_id: str):
    """Process a notification in the background"""
    try:
        logger.info(f"Starting to process notification: {notification_id}")

        # Convert string ID to ObjectId
        object_id = ObjectId(notification_id)
        notification = notification_collection.find_one({"_id": object_id})

        if not notification:
            logger.error(f"Notification not found: {notification_id}")
            return

        logger.info(f"Found notification, sending email to: {notification['recipient_email']}")
        logger.info(f"Email subject: {notification['subject']}")
        logger.info(f"Email content: {notification['content'][:100]}...") # Log first 100 chars of content

        success = await send_email(
            notification["recipient_email"],
            notification["subject"],
            notification["content"]
        )

        if success:
            logger.info(f"Email sent successfully for notification: {notification_id}")
            status = NotificationStatus.SENT
        else:
            logger.error(f"Failed to send email for notification: {notification_id}")
            status = NotificationStatus.FAILED

        update_data = {
            "status": status,
            "sent_at": datetime.now() if success else None,
            "retry_count": notification.get("retry_count", 0) + 1
        }

        notification_collection.update_one(
            {"_id": object_id},  # Use ObjectId here too
            {"$set": update_data}
        )
        logger.info(f"Updated notification status to: {status}")

    except Exception as e:
        logger.error(f"Error processing notification {notification_id}: {str(e)}")
        logger.exception("Detailed error stack:")
        try:
            # Try to update status even if processing failed
            notification_collection.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {
                    "status": NotificationStatus.FAILED,
                    "error_message": str(e)
                }}
            )
        except Exception as update_error:
            logger.error(f"Failed to update error status: {str(update_error)}")

@router.get("/check/{notification_id}", response_model=dict)
async def check_notification_status(notification_id: str):
    """Check the status of a specific notification"""
    try:
        notification = notification_collection.find_one({"_id": ObjectId(notification_id)})
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {
            "id": str(notification["_id"]),
            "status": notification["status"],
            "recipient_email": notification["recipient_email"],
            "sent_at": notification.get("sent_at"),
            "retry_count": notification.get("retry_count", 0),
            "subject": notification["subject"],
            "error_message": notification.get("error_message")  # Include any error message
        }
    except Exception as e:
        logger.error(f"Error checking notification status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))