import pika
from datetime import datetime
from config import get_rabbitmq_uri

connection = None
channel = None


def connect_rabbitmq():
    global connection, channel
    
    try:
        if connection and channel:
            print(f"[{datetime.now().isoformat()}] [INFO] RabbitMQ already connected")
            return connection, channel

        rabbitmq_uri = get_rabbitmq_uri()
        print(f"[{datetime.now().isoformat()}] [INFO] Connecting to RabbitMQ...")
        
        params = pika.URLParameters(rabbitmq_uri)
        params.heartbeat = 60
        params.blocked_connection_timeout = 30
        
        connection = pika.BlockingConnection(params)
        
        connection.add_on_close_callback(_on_connection_closed)
        connection.add_on_open_error_callback(_on_connection_error)
        
        channel = connection.channel()
        
        print(f"[{datetime.now().isoformat()}] [INFO] RabbitMQ Connected successfully")
        print(f"[{datetime.now().isoformat()}] [INFO] RabbitMQ Channel created successfully")

        return connection, channel
    except Exception as error:
        print(f"[{datetime.now().isoformat()}] [ERROR] Failed to connect to RabbitMQ: {error}")
        connection = None
        channel = None
        raise


def _on_connection_closed(connection_unused, reason):
    global connection, channel
    print(f"[{datetime.now().isoformat()}] [WARN] RabbitMQ connection closed: {reason}")
    connection = None
    channel = None


def _on_connection_error(connection_unused, error):
    global connection, channel
    print(f"[{datetime.now().isoformat()}] [ERROR] RabbitMQ connection error: {error}")
    connection = None
    channel = None


def get_channel():
    if not channel:
        raise RuntimeError("RabbitMQ channel is not initialized. Call connect_rabbitmq() first.")
    return channel


def is_connected():
    return connection is not None and channel is not None


def close_rabbitmq():
    global connection, channel
    try:
        if channel:
            channel.close()
            channel = None
            print(f"[{datetime.now().isoformat()}] [INFO] RabbitMQ channel closed")
        if connection:
            connection.close()
            connection = None
            print(f"[{datetime.now().isoformat()}] [INFO] RabbitMQ connection closed")
    except Exception as error:
        print(f"[{datetime.now().isoformat()}] [ERROR] Error closing RabbitMQ connection: {error}")
