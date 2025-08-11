from twilio.rest import Client
import os
from dotenv import load_dotenv
import re
import logging

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
# Default to mock mode for local development
# Set MOCK_SMS=false for production
mock_sms = os.getenv('MOCK_SMS', 'true').lower() == 'true'

logger = logging.getLogger(__name__)

if not mock_sms and account_sid and auth_token:
    client = Client(account_sid, auth_token)
else:
    client = None
    if mock_sms:
        logger.info(
            "SMS Service running in MOCK mode - "
            "messages will be logged instead of sent"
        )


def send_welcome_sms(to_number: str, group_name: str):
    """Send welcome SMS when user joins a group"""
    body = (
        f"Welcome to the '{group_name}' chat! "
        f"Reply to this number to send messages to the group."
    )

    if client:
        message = client.messages.create(
            body=body,
            from_=twilio_phone_number,
            to=to_number
        )
        return message.sid
    else:
        logger.info(f"[MOCK SMS] To: {to_number}")
        logger.info(f"[MOCK SMS] Message: {body}")
        return "mock-message-id"


def send_group_message(
    to_number: str, from_name: str, content: str,
    group_name: str, group_phone_number: str = None
):
    """Send group message to a member"""
    body = f"[{group_name}] {from_name}: {content}"
    from_number = group_phone_number or twilio_phone_number

    if client:
        message = client.messages.create(
            body=body,
            from_=from_number,
            to=to_number
        )
        return message.sid
    else:
        logger.info(f"[MOCK SMS] To: {to_number}")
        logger.info(f"[MOCK SMS] From: {from_number}")
        logger.info(f"[MOCK SMS] Message: {body}")
        return "mock-message-id"


def send_welcome_sms_with_phone(
    to_number: str, group_name: str, group_phone_number: str
):
    """Send welcome SMS with specific group phone number"""
    body = (
        f"Welcome to the '{group_name}' chat! "
        f"Reply to this number to send messages to the group."
    )

    if client:
        message = client.messages.create(
            body=body,
            from_=group_phone_number,
            to=to_number
        )
        return message.sid
    else:
        logger.info(f"[MOCK SMS] To: {to_number}")
        logger.info(f"[MOCK SMS] From: {group_phone_number}")
        logger.info(f"[MOCK SMS] Message: {body}")
        return "mock-message-id"


def send_otp_sms(to_number: str, otp_code: str):
    """Send OTP verification SMS"""
    body = (
        f"Your SMS Chat verification code is: {otp_code}. "
        f"Valid for 10 minutes."
    )

    if client:
        message = client.messages.create(
            body=body,
            from_=twilio_phone_number,
            to=to_number
        )
        return message.sid
    else:
        logger.info(f"[MOCK SMS] To: {to_number}")
        logger.info(f"[MOCK SMS] OTP: {body}")
        return "mock-message-id"


def parse_sms_command(body: str):
    """Parse SMS to extract group name if user is in multiple groups
    Format: @groupname message or just message if in single group
    """
    # Match @"group name" message or @group_name message
    # First try quoted group names: @"Group Name" message
    quoted_match = re.match(r'^@"([^"]+)"\s+(.+)$', body.strip())
    if quoted_match:
        return quoted_match.group(1), quoted_match.group(2)

    # For unquoted group names with spaces, we need to be smarter
    # Try to match known patterns - look for @GroupName or @Group Name
    # followed by at least 2 words
    unquoted_match = re.match(
        r'^@([A-Za-z][A-Za-z\s]*?)\s+([a-zA-Z].+)$',
        body.strip()
    )
    if unquoted_match:
        group_name = unquoted_match.group(1).strip()
        message = unquoted_match.group(2)
        # If the group name ends with a common word that might be part
        # of the message, adjust
        words = group_name.split()
        if len(words) > 1:
            return group_name, message
        else:
            # Single word group name
            return group_name, message

    return None, body
