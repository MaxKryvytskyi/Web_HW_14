from pathlib import Path
from decouple import config
from pydantic import EmailStr
from fastapi import HTTPException
from fastapi_mail.errors import ConnectionErrors
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from src.services.auth import auth_service

 
conf = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME"),
    MAIL_PASSWORD=config("MAIL_PASSWORD"),
    MAIL_FROM=config("MAIL_FROM"),
    MAIL_PORT=config("MAIL_PORT"),
    MAIL_SERVER=config("MAIL_SERVER"),
    MAIL_FROM_NAME=config("MAIL_FROM_NAME"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)


async def send_resets_password(email: EmailStr, username: str, host: str):
    try:
        print(email)
        token_reset_password = auth_service.create_email_reset_password_token({"sub": email})
        print(token_reset_password)
        # message = MessageSchema(
        #     subject="Confirm reset password",
        #     recipients=[email],
        #     template_body={"host": host, "username": username, "token": token_reset_password},
        #     subtype=MessageType.html
        # )

        # fm = FastMail(conf)
        # await fm.send_message(message, template_name="password_reset_email.html")
    except ConnectionErrors as err:
        raise HTTPException(status_code=500, detail=f"Failed to send an email: {str(err)}")
    return {"message": "Email has been sent successfully!"}