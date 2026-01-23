import sys
import threading
import signal
from datetime import datetime
from rabbitmq.connection import connect_rabbitmq, close_rabbitmq
from consumers.verification_consumer import start_verification_consumer
from consumers.contact_consumer import start_contact_consumer


def run_verification_consumer():
    try:
        start_verification_consumer()
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] [VERIFICATION] Consumer error: {e}")


def run_contact_consumer():
    try:
        start_contact_consumer()
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] [CONTACT] Consumer error: {e}")


def main():
    if len(sys.argv) > 1:
        consumer_type = sys.argv[1].lower()
        
        connect_rabbitmq()
        
        if consumer_type == "verification":
            print(f"[{datetime.now().isoformat()}] [MAIN] Starting verification consumer only...")
            start_verification_consumer()
        elif consumer_type == "contact":
            print(f"[{datetime.now().isoformat()}] [MAIN] Starting contact consumer only...")
            start_contact_consumer()
        else:
            print(f"[{datetime.now().isoformat()}] [ERROR] Unknown consumer type: {consumer_type}")
            print("Usage: python main.py [verification|contact]")
            sys.exit(1)
    else:
        print(f"[{datetime.now().isoformat()}] [MAIN] Starting both consumers...")
        
        connect_rabbitmq()
        
        verification_thread = threading.Thread(target=run_verification_consumer, daemon=True)
        contact_thread = threading.Thread(target=run_contact_consumer, daemon=True)
        
        verification_thread.start()
        contact_thread.start()
        
        def signal_handler(sig, frame):
            print(f"\n[{datetime.now().isoformat()}] [MAIN] Shutting down...")
            close_rabbitmq()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            verification_thread.join()
            contact_thread.join()
        except KeyboardInterrupt:
            signal_handler(None, None)


if __name__ == "__main__":
    main()
