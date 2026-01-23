import json
from datetime import datetime
from rabbitmq.connection import get_channel
from mail.sender import send_email
from mail.templates import format_verification_email


def handle_verification_message(ch, method, properties, body):
    try:
        payload = json.loads(body.decode("utf-8"))
        user_id = payload.get("userID")
        email = payload.get("email")
        token = payload.get("token")

        if not email or not token:
            raise ValueError("Missing required fields: email or token")

        email_body = format_verification_email(token)
        send_email(email, "Verify your email", email_body)
        
        print(f"[{datetime.now().isoformat()}] [VERIFICATION] Sent verification email -> userId={user_id} email={email}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[{datetime.now().isoformat()}] [VERIFICATION] ERROR: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_verification_consumer():
    channel = get_channel()
    
    exchange = "forum.events"
    queue_name = "email_service_queue"
    routing_key = "user.verify_email"
    
    channel.exchange_declare(exchange=exchange, exchange_type="topic", durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    
    channel.queue_bind(
        exchange=exchange,
        queue=queue_name,
        routing_key=routing_key,
    )
    
    channel.basic_qos(prefetch_count=1)
    
    print(f"[{datetime.now().isoformat()}] [VERIFICATION] Consumer started - waiting for messages on queue '{queue_name}'...")
    channel.basic_consume(queue=queue_name, on_message_callback=handle_verification_message)
    
    channel.start_consuming()
