from pathlib import Path
from typing import Any
from typing import Dict

import emails
import ulid
from emails.template import JinjaTemplate

from app.core.config import settings


def get_id() -> str:
    return ulid.new().str.lower()


def send_email(
    email_to: Any,
    subject: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / html_template) as f:
        template_str = f.read()

    message = emails.Message(
        subject=JinjaTemplate(subject),
        html=JinjaTemplate(template_str),
        mail_from=(settings.SMTP_USER, settings.SMTP_USER),
    )

    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    print(f"send email result: {response}")
    return response.status_code
