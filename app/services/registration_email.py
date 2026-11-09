import logging
import re
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from html import escape
from typing import Callable, Literal, Optional

from pymongo.errors import PyMongoError

from app.core import configuration
from app.models.email_log import EmailLog
from app.models.email_notification import PLACEHOLDER_PATTERN, RegistrationEmailConfig
from app.models.user import User
from app.services.email_log import EmailLogService
from app.utils import PyObjectId


logger = logging.getLogger(__name__)


def user_email_values(user: User) -> dict[str, str]:
    return {
        "username": user.username,
        "given_name": user.given_name or "",
        "family_name": user.family_name or "",
        "email": user.email,
    }


def render_registration_email(template: str, user: User) -> str:
    values = user_email_values(user)

    def replace(match: re.Match[str]) -> str:
        # All placeholders are validated before the template is saved or loaded.
        return escape(values[match.group(1)], quote=True)

    return PLACEHOLDER_PATTERN.sub(replace, template)


def send_registration_email(html: str, subject: str, recipient: str) -> None:
    if not configuration.SMTP_HOST or not configuration.SMTP_FROM or not recipient:
        raise ValueError("SMTP host, sender and recipient email are required")
    if bool(configuration.SMTP_USERNAME) != bool(configuration.SMTP_PASSWORD):
        raise ValueError("SMTP username and password must both be configured")
    if configuration.SMTP_SECURITY not in {"starttls", "ssl"}:
        raise ValueError("SMTP_SECURITY must be starttls or ssl")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = configuration.SMTP_FROM
    message["To"] = recipient
    message.set_content("Tu registro fue recibido. Consulta la versión HTML de este mensaje.")
    message.add_alternative(html, subtype="html")

    context = ssl.create_default_context()
    if configuration.SMTP_SECURITY == "ssl":
        client = smtplib.SMTP_SSL(
            configuration.SMTP_HOST, configuration.SMTP_PORT,
            timeout=configuration.SMTP_TIMEOUT, context=context,
        )
    else:
        client = smtplib.SMTP(
            configuration.SMTP_HOST, configuration.SMTP_PORT,
            timeout=configuration.SMTP_TIMEOUT,
        )
    with client:
        if configuration.SMTP_SECURITY == "starttls":
            client.starttls(context=context)
        if configuration.SMTP_USERNAME:
            client.login(configuration.SMTP_USERNAME, configuration.SMTP_PASSWORD)
        client.send_message(message)


def notify_registration(
    get_config: Callable[[PyObjectId], RegistrationEmailConfig | None],
    item_id: PyObjectId,
    registration_id: PyObjectId | None,
    item_type: Literal["event", "activity"],
    title: str,
    user: User,
    event_id: Optional[PyObjectId] = None,
) -> None:
    subject = f"Registro: {title}"
    html = None
    try:
        config = get_config(item_id)
        if config is None:
            raise ValueError("Registration email configuration could not be loaded")
        if not config.email_enabled:
            return
        if not config.email_template:
            raise ValueError("Enabled registration email requires an HTML template")
        html = render_registration_email(config.email_template, user)
        send_registration_email(html, subject, user.email)
    except (PyMongoError, smtplib.SMTPException, OSError, ValueError) as error:
        logger.error(
            "Registration %s for %s %s was saved, but email notification failed (%s)",
            registration_id, item_type, item_id, type(error).__name__,
        )
        error_text = f"{type(error).__name__}: {error}"[:1000]
        _save_attempt(
            user, item_type, item_id, event_id, registration_id, subject, html,
            success=False, error=error_text,
        )
        return
    _save_attempt(
        user, item_type, item_id, event_id, registration_id, subject, html, success=True
    )


def _save_attempt(
    user: User,
    item_type: Literal["event", "activity"],
    item_id: PyObjectId,
    event_id: Optional[PyObjectId],
    registration_id: Optional[PyObjectId],
    subject: str,
    html: Optional[str],
    success: bool,
    error: Optional[str] = None,
) -> None:
    try:
        EmailLogService.insert(EmailLog(
            date=datetime.now(timezone.utc),
            email=user.email,
            user=user.id,
            username=user.username,
            item_type=item_type,
            event=item_id if item_type == "event" else event_id,
            activity=item_id if item_type == "activity" else None,
            registration=registration_id,
            subject=subject,
            template=html,
            success=success,
            error=error,
        ))
    except PyMongoError as log_error:
        # Losing the audit record must not undo a saved registration.
        logger.error(
            "Could not save email attempt for registration %s (%s)",
            registration_id, type(log_error).__name__,
        )
