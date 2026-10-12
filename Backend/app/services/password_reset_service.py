import logging
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode

from app.core.config import settings

logger = logging.getLogger(__name__)


def email_password_reset(recipient: str, token: str) -> None:
    if not settings.smtp_host or not settings.smtp_sender_email:
        logger.error("Password reset email was not sent: SMTP_HOST and SMTP_SENDER_EMAIL must be configured.")
        return

    reset_url = f"{settings.frontend_url.rstrip('/')}/reset-password?{urlencode({'token': token})}"
    message = EmailMessage()
    message["Subject"] = "Reset your PageTurners password"
    message["From"] = settings.smtp_sender_email
    message["To"] = recipient
    message.set_content(
        "We received a request to reset your PageTurners password.\n\n"
        f"Use this one-time link within 30 minutes:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                context=ssl.create_default_context(),
                timeout=15,
            ) as server:
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password or "")
                server.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password or "")
                server.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Failed to deliver a PageTurners password reset email.")
