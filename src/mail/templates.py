import os

def format_verification_email(token,code):
    app_url = os.environ.get("REACT_BASE_URL","http://127.0.0.1:5173")
    verify_link = f"{app_url}/users/verify?token={token}"
    
    return f"""Hello!

This is your verification code for your account:
    {code}

Alternatively, click this link to verify your email:

{verify_link}

If you didn't create this account, ignore this email.
"""


def format_contact_confirmation_email(subject, message):
    return f"""Hello!

Thank you for contacting us. We have received your message:

Subject: {subject}

Message:
{message}

We will get back to you as soon as possible.

Best regards,
Forum Team
"""
