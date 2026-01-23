# forum-email-service

A Python microservice that handles email notifications for a forum application. The service consumes messages from RabbitMQ and sends emails via SMTP for user verification and contact form confirmations.

## Features

- **Verification Email Consumer**: Sends email verification links to users when they register
- **Contact Form Consumer**: Sends confirmation emails to users when they submit contact forms
- **Modular Architecture**: Clean separation of concerns with dedicated modules for RabbitMQ, email, and consumers
- **Dual Consumer Support**: Both consumers can run simultaneously without interference
- **CloudAMQP Integration**: Uses CloudAMQP for reliable message queue management
- **Proper Acknowledgment**: Messages are only acknowledged after successful email delivery

## Project Structure

```
src/
├── main.py                    # Entry point to run both consumers
├── config.py                  # Shared configuration and env loading
├── rabbitmq/
│   ├── __init__.py
│   └── connection.py          # CloudAMQP connection logic
├── email/
│   ├── __init__.py
│   ├── sender.py              # Shared SMTP email sending logic
│   └── templates.py           # Email templates
└── consumers/
    ├── __init__.py
    ├── verification_consumer.py  # Verification email consumer
    └── contact_consumer.py       # Contact form consumer
```

## Setup

### Prerequisites

- Python 3.7+
- CloudAMQP account (or RabbitMQ instance)
- SMTP server credentials

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd forum-email-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
# CloudAMQP Connection (shared by both consumers)
RABBITMQ_URI=amqps://user:password@host.cloudamqp.com/vhost

# SMTP Configuration (shared by both consumers)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SMTP_FROM=noreply@example.com

# App Configuration
APP_BASE_URL=http://127.0.0.1:3000
```

## Usage

### Run Both Consumers

Start both the verification and contact consumers simultaneously:

```bash
python src/main.py
```

### Run Individual Consumers

Run only the verification consumer:
```bash
python src/main.py verification
```

Run only the contact consumer:
```bash
python src/main.py contact
```

## Consumers

### Verification Consumer

- **Exchange**: `forum.events` (topic)
- **Queue**: `email_service_queue`
- **Routing Key**: `user.verify_email`
- **Payload Format**:
  ```json
  {
    "userID": "123",
    "email": "user@example.com",
    "token": "verification-token"
  }
  ```
- **Action**: Sends verification email with a link containing the token

### Contact Consumer

- **Exchange**: `contact_exchange` (topic)
- **Queue**: `email_notification_queue`
- **Routing Key**: `#` (all messages)
- **Payload Format**:
  ```json
  {
    "subject": "Contact Form Subject",
    "email": "user@example.com",
    "message": "User's message content"
  }
  ```
- **Action**: Sends confirmation email to the user acknowledging receipt of their contact form submission

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `RABBITMQ_URI` | CloudAMQP connection string | Yes |
| `SMTP_HOST` | SMTP server hostname | Yes |
| `SMTP_PORT` | SMTP server port (typically 587) | Yes |
| `SMTP_USER` | SMTP username | Yes |
| `SMTP_PASS` | SMTP password/app password | Yes |
| `SMTP_FROM` | Email address to send from | Yes |
| `APP_BASE_URL` | Base URL for verification links | No (defaults to http://127.0.0.1:3000) |

## Error Handling

- Messages are only acknowledged (`ack`) after successful email delivery
- Failed email sends result in `nack` with requeue, allowing retry
- Connection errors are logged with timestamps
- Both consumers run in separate threads to prevent interference

## Logging

The service uses ISO timestamped logging with prefixes:
- `[VERIFICATION]` - Verification consumer logs
- `[CONTACT]` - Contact consumer logs
- `[MAIN]` - Main application logs
- `[INFO]`, `[ERROR]`, `[WARN]` - Log levels

## Dependencies

- `pika` - RabbitMQ client library
- `python-dotenv` - Environment variable management