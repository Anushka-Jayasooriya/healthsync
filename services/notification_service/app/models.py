from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class Notification(BaseModel):
    recipient_email: EmailStr
    subject: str
    content: str
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    retry_count: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }