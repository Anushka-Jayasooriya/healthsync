# app/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings
import logging

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, content: str) -> bool:
    """Send email using smtplib"""
    try:
        logger.info(f"Preparing email to: {to_email}")
        logger.info(f"Subject: {subject}")

        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = settings.SMTP_USERNAME
        message['To'] = to_email

        html_part = MIMEText(content, 'html')
        message.attach(html_part)

        logger.info(f"Connecting to SMTP server: {settings.SMTP_HOST}:{settings.SMTP_PORT}")

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            logger.info("Starting TLS connection...")
            server.starttls()
            logger.info("Logging into SMTP server...")
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            logger.info("Sending email...")
            server.send_message(message)

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        logger.exception("Detailed error:")
        return False