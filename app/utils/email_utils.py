# app/utils/email_utils.py
import time


def send_email(to: str, subject: str, body: str):
    """Mock sync email sender (used in auth verification/reset flows)."""
    print(f"📧 Sending email to {to}...")
    time.sleep(1)
    print(f"✅ Email sent: {subject}")


# Backward compatibility alias
send_email_background = send_email
