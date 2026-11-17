
import os
import re

from dotenv import load_dotenv
from mailosaur import MailosaurClient
from mailosaur.models import SearchCriteria

load_dotenv()


def get_email_otp(test_email):
    api_key = os.environ["MAILOSAUR_API_KEY"]
    server_id = os.environ["MAILOSAUR_SERVER_ID"]

    client = MailosaurClient(api_key)

    criteria = SearchCriteria()
    criteria.sent_to = test_email

    # Wait for the matching verification email
    message = client.messages.get(
        server_id,
        criteria,
        timeout=60000
    )

    # Extract OTP if supported by email format
    codes = message.text.codes if message.text else None

    if codes:
        return codes[0].value

    # Fallback for plain-text messages
    body = message.text.body if message.text else ""
    match = re.search(r"\b\d{6}\b", body)

    if not match:
        raise ValueError("No six-digit OTP found in email")

    return match.group()
