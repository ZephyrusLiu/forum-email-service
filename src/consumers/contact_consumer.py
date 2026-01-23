import json
from datetime import datetime
from rabbitmq.connection import get_channel
from email.sender import send_email
from email.templates import format_contact_confirmation_email


def handle_contact_message(ch, method, properties, body):
    try:
        payload = json.loads(body.decode("utf-8"))
        subject = payload.get("subject")
        email = payload.get("email")
        message = payload.get("message")

        if not email or not subject or not message:
            raise ValueError("Missing required fields: subject, email, or message")

        email_body = format_contact_confirmation_email(subject, message)
        send_email(email, "We've received your message", email_body)
        
        print(f"[{datetime.now().isoformat()}] [CONTACT] Sent confirmation email -> email={email} subject={subject}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[{datetime.now().isoformat()}] [CONTACT] ERROR: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_contact_consumer():
    channel = get_channel()
    
    exchange = "contact_exchange"
    queue_name = "email_notification_queue"
    
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    
    channel.queue_bind(
        exchange=exchange,
        queue=queue_name,
        routing_key="#",
    )
    
    channel.basic_qos(prefetch_count=1)
    
    print(f"[{datetime.now().isoformat()}] [CONTACT] Consumer started - waiting for messages on queue '{queue_name}'...")
    channel.basic_consume(queue=queue_name, on_message_callback=handle_contact_message)
    
    channel.start_consuming()
