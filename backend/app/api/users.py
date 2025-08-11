from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.models import User
from app.models.schemas import UserCreate, UserResponse
from app.services.otp_service import create_otp_verification, verify_otp
from pydantic import BaseModel

router = APIRouter()


class PhoneNumberRequest(BaseModel):
    phone_number: str


class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str


class RegisterRequest(BaseModel):
    phone_number: str
    name: str
    otp_code: str


@router.post("/send-otp")
def send_otp(request: PhoneNumberRequest, db: Session = Depends(get_db)):
    """Send OTP to phone number for registration/login"""
    create_otp_verification(db, request.phone_number)
    return {"message": "OTP sent successfully"}


@router.post("/register", response_model=UserResponse)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user with OTP verification"""
    # Verify OTP
    if not verify_otp(db, request.phone_number, request.otp_code):
        raise HTTPException(
            status_code=400, detail="Invalid or expired OTP"
        )

    # Check if user already exists
    db_user = db.query(User).filter(
        User.phone_number == request.phone_number
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Phone number already registered"
        )

    # Create user
    db_user = User(name=request.name, phone_number=request.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=UserResponse)
def login_user(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Login user with OTP verification"""
    # Verify OTP
    if not verify_otp(db, request.phone_number, request.otp_code):
        raise HTTPException(
            status_code=400, detail="Invalid or expired OTP"
        )

    # Get user
    db_user = db.query(User).filter(
        User.phone_number == request.phone_number
    ).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


# Legacy endpoint for backward compatibility (tests use this)
@router.post("/", response_model=UserResponse)
def create_user_legacy(user: UserCreate, db: Session = Depends(get_db)):
    """Create user without OTP (legacy endpoint for tests)"""
    db_user = db.query(User).filter(
        User.phone_number == user.phone_number
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Phone number already registered"
        )

    db_user = User(name=user.name, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/phone/{phone_number}", response_model=UserResponse)
def get_user_by_phone(phone_number: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/groups", response_model=List[int])
def get_user_groups(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Return list of group IDs the user is a member of
    return [group.id for group in user.groups]
