from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import List

from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail
from fastapi_mail import MessageSchema
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape
from pydantic import EmailStr

from backend.core.conf import settings
# from backend.common.enums import Token_type
# from app.core.security import generate_secret_token
# from app.models import User
# from backend.schemas.token import Token

env = Environment(
    loader=PackageLoader("backend", f"{settings.EMAIL_TEMPLATES_DIR}/"),
    autoescape=select_autoescape(
        enabled_extensions=("html", "xml"), default_for_string=True
    ),
)


class Email:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.EMAILS_FROM_EMAIL,
            MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=settings.SMTP_TLS,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=False,
        )
        pass

    async def send_login_mail(
        self, email: EmailStr, url: str | None = None, name: str | None = None
    ):
        pass
        

    async def send_reset_password_mail(
        self, email: EmailStr, url: str | None = None, name: str | None = None
    ):
        pass

    async def send_verify_mail(
        self, email: EmailStr, url: str | None = None, name: str | None = None
    ):
        pass

    async def send_welcome_mail(
        self, email: EmailStr, url: str | None = None, name: str | None = None
    ):
        template = env.get_template("welcome-one.html")
       
        subject = "Bienvenue sur Boilerplate"
        html = template.render(
            subject=subject,
            link=url,
            email=email
        )
        message = MessageSchema(
            subject=subject, recipients=[email], body=html, subtype="html"
        )

        fm = FastMail(self.conf)
        await fm.send_message(message)

    async def send_forgot_password_mail(
        self, email: EmailStr, url: str | None = None, name: str | None = None
    ):
        template = env.get_template("reset-password.html")
        subject = "Réinitialisation du mot de passe"
        html = template.render(
            subject=subject,
            link=url,
            email=email
        )
        message = MessageSchema(
            subject=subject, recipients=[email], body=html, subtype="html"
        )

        fm = FastMail(self.conf)
        await fm.send_message(message)

    async def send_change_password_mail(
        self, email: EmailStr, url: str | None = None, name: str | None = None
    ):
        pass

    async def send_change_email_mail(
        self, email: EmailStr, url: str | None = None, name: str | None = None
    ):
        pass

email_service = Email()