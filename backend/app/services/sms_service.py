from twilio.rest import Client
import os
from dotenv import load_dotenv
import re
import logging

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
mock_sms = os.getenv('MOCK_SMS', '').lower() == 'true'

logger = logging.getLogger(__name__)

if not mock_sms and account_sid and auth_token:
    client = Client(account_sid, auth_token)
else:
    client = None
    if mock_sms:
        logger.info("SMS Service running in MOCK mode - messages will be logged instead of sent")

def send_welcome_sms(to_number: str, group_name: str):
    """Send welcome SMS when user joins a group"""
    body = f"Welcome to the '{group_name}' chat! Reply to this number to send messages to the group."
    
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

def send_group_message(to_number: str, from_name: str, content: str, group_name: str):
    """Send group message to a member"""
    body = f"[{group_name}] {from_name}: {content}"
    
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

def parse_sms_command(body: str):
    """Parse SMS to extract group name if user is in multiple groups
    Format: @groupname message or just message if in single group
    """
    match = re.match(r'^@(\w+)\s+(.+)$', body.strip())
    if match:
        return match.group(1), match.group(2)
    return None, body