from email.message import EmailMessage

from pydantic import EmailStr

from app.config import settings


def create_booking_confirmation_template(booking: dict, email_to: EmailStr):
    """Message template to send about successful booking"""
    email = EmailMessage()

    email["subject"] = "Confirmation of room booking"
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <h1>You've booked a room</h1>
            ou booked a room from {booking["date_from"]}
            to {booking["date_to"]}
        """,
        subtype="html",
    )
    return email
