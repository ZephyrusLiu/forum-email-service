import smtplib
from email.message import EmailMessage
from datetime import datetime
from config import get_smtp_config


def send_email(to_email, subject, body):
    smtp_config = get_smtp_config()
    
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_config["from_email"]
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["user"], smtp_config["password"])
            server.send_message(msg)
        print(f"[{datetime.now().isoformat()}] [INFO] Email sent successfully to {to_email}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] [ERROR] Failed to send email to {to_email}: {e}")
        raise
