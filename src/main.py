import os
import json
import pika
from dotenv import load_dotenv
from pathlib import Path

import smtplib
from email.message import EmailMessage

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

def send_verification_email(to_email, token):
    verify_link = f"{os.environ.get('APP_BASE_URL', 'http://127.0.0.1:3000')}/users/verify?token={token}"

    msg = EmailMessage()
    msg["Subject"] = "Verify your email"
    msg["From"] = os.environ["SMTP_FROM"]
    msg["To"] = to_email

    msg.set_content(
            f"""Hello!

Click this link to verify your email:

{verify_link}

If you didn’t create this account, ignore this email.
"""
)

    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def handle_message(ch, method, properties, body):
    try:
        payload = json.loads(body.decode("utf-8"))
        user_id = payload.get("userID")
        email = payload.get("email")
        token = payload.get("token")

        send_verification_email(email, token)
        print(f"[EMAIL SERVICE] send verification email -> userId={user_id} email={email}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[EMAIL SERVICE] ERROR: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    creds = pika.PlainCredentials(
        os.environ["RABBITMQ_USER"],
        os.environ["RABBITMQ_PASS"],
    )

    params = pika.ConnectionParameters(
        host=os.environ["RABBITMQ_HOST"],
        virtual_host=os.environ.get("RABBITMQ_VHOST", "/"),
        credentials=creds,
        heartbeat=60,
        blocked_connection_timeout=30,
    )

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    exchange = os.environ.get("RABBITMQ_EXCHANGE", "forum.events")
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)

    queue_name = "email_service_queue"
    channel.queue_declare(queue=queue_name, durable=True)

    channel.queue_bind(
        exchange=exchange,
        queue=queue_name,
        routing_key="user.verify_email",
    )

    channel.basic_qos(prefetch_count=1)

    print("[EMAIL SERVICE] waiting for messages...")
    channel.basic_consume(queue=queue_name, on_message_callback=handle_message)

    channel.start_consuming()


if __name__ == "__main__":
    main()

