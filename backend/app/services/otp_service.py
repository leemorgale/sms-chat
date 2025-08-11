import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.phone_pool import OTPVerification
from app.services.sms_service import send_otp_sms
import logging
import os

logger = logging.getLogger(__name__)


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP code"""
    # In mock mode, always return 111111
    if os.getenv('MOCK_SMS', 'true').lower() == 'true':
        return '111111'
    return ''.join(random.choices(string.digits, k=length))


def create_otp_verification(db: Session, phone_number: str) -> str:
    """Create OTP verification record and send SMS"""
    # Delete any existing unverified OTPs for this number
    db.query(OTPVerification).filter(
        OTPVerification.phone_number == phone_number,
        OTPVerification.verified == 0
    ).delete()

    # Generate new OTP
    otp_code = generate_otp()
    # 10 minute expiry
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    # Create verification record
    verification = OTPVerification(
        phone_number=phone_number,
        otp_code=otp_code,
        expires_at=expires_at
    )
    db.add(verification)
    db.commit()

    # Send OTP via SMS
    send_otp_sms(phone_number, otp_code)

    logger.info(f"OTP sent to {phone_number}")
    return otp_code


def verify_otp(db: Session, phone_number: str, otp_code: str) -> bool:
    """Verify OTP code"""
    verification = db.query(OTPVerification).filter(
        OTPVerification.phone_number == phone_number,
        OTPVerification.otp_code == otp_code,
        OTPVerification.verified == 0,
        OTPVerification.expires_at > datetime.utcnow()
    ).first()

    if not verification:
        return False

    # Mark as verified
    verification.verified = 1
    db.commit()

    return True


def get_available_phone_number(db: Session):
    """Get an available phone number from the pool"""
    from app.models.phone_pool import PhoneNumber, PhoneStatus

    phone = db.query(PhoneNumber).filter(
        PhoneNumber.status == PhoneStatus.AVAILABLE
    ).first()

    return phone


def assign_phone_to_group(db: Session, phone_id: int, group_id: int):
    """Assign a phone number to a group"""
    from app.models.phone_pool import PhoneNumber, PhoneStatus

    phone = db.query(PhoneNumber).filter(PhoneNumber.id == phone_id).first()
    if phone:
        phone.status = PhoneStatus.ASSIGNED
        phone.group_id = group_id
        phone.assigned_at = datetime.utcnow()
        db.commit()
