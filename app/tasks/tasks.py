import smtplib
from pathlib import Path

from PIL import Image
from pydantic import EmailStr

from app.config import settings
from app.tasks.celery_setup import celery
from app.tasks.email_templates import create_booking_confirmation_template


@celery.task
def process_pic(path: str):
    """Task for compressing downloaded images"""
    img_path = Path(path)
    img = Image.open(img_path)
    img_resized_large = img.resize((1000, 500))
    img_resized_small = img.resize((200, 100))
    img_resized_large.save(f"app/static/images/resized_1000_500_{img_path.name}")
    img_resized_small.save(f"app/static/images/resized_200_100_{img_path.name}")


@celery.task
def send_booking_confirmation_email(booking: dict, email_to: EmailStr):
    """Task for sending messages to mail about successful booking"""
    msg_content = create_booking_confirmation_template(
        booking=booking, email_to=email_to
    )
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)
