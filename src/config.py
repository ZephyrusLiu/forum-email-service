import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def get_rabbitmq_uri():
    uri = os.environ.get("RABBITMQ_URI")
    if not uri:
        raise ValueError("RABBITMQ_URI environment variable is not set")
    return uri


def get_smtp_config():
    return {
        "host": os.environ["SMTP_HOST"],
        "port": int(os.environ["SMTP_PORT"]),
        "user": os.environ["SMTP_USER"],
        "password": os.environ["SMTP_PASS"],
        "from_email": os.environ["SMTP_FROM"],
    }


def get_app_base_url():
    return os.environ.get("APP_BASE_URL", "http://127.0.0.1:3000")
