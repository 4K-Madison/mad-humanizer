"""Email sending service using Gmail SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import structlog

from app.config import settings

logger = structlog.get_logger()


async def send_verification_email(to_email: str, code: str) -> bool:
    """Send a verification code email via Gmail SMTP.

    Uses smtplib in a thread to avoid blocking the async event loop.
    """
    import asyncio

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_email_sync, to_email, code)


def _send_email_sync(to_email: str, code: str) -> bool:
    """Synchronous email send (runs in executor)."""
    subject = "MAD-HUMANIZER — Email Verification Code"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <h2 style="color: #1a1a1a; margin-bottom: 8px;">MAD-HUMANIZER : Verify your email</h2>
        <p style="color: #666; font-size: 14px;">
            Use the verification code below to complete your MAD-HUMANIZER signup.
            This code expires in {settings.VERIFICATION_CODE_EXPIRY_MINUTES} minutes.
        </p>
        <div style="background: #f4f4f5; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1a1a1a;">
                {code}
            </span>
        </div>
        <p style="color: #999; font-size: 12px;">
            If you didn't request this, you can safely ignore this email.
        </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(f"Your MAD-HUMANIZER verification code is: {code}", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
        logger.info("Verification email sent", to=to_email)
        return True
    except Exception as exc:
        logger.error("Failed to send verification email", to=to_email, error=str(exc))
        return False
