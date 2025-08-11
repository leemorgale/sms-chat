from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.phone_pool import PhoneNumber, PhoneStatus
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class PhoneNumberCreate(BaseModel):
    phone_number: str
    twilio_sid: Optional[str] = None


class PhoneNumberResponse(BaseModel):
    id: int
    phone_number: str
    twilio_sid: Optional[str] = None
    status: PhoneStatus
    group_id: Optional[int] = None
    created_at: datetime
    assigned_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/phone-numbers", response_model=PhoneNumberResponse)
def register_phone_number(
    phone: PhoneNumberCreate, db: Session = Depends(get_db)
):
    """Register a new Twilio phone number in the pool"""
    existing = db.query(PhoneNumber).filter(
        PhoneNumber.phone_number == phone.phone_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Phone number already registered"
        )

    db_phone = PhoneNumber(
        phone_number=phone.phone_number,
        twilio_sid=phone.twilio_sid,
        status=PhoneStatus.AVAILABLE
    )
    db.add(db_phone)
    db.commit()
    db.refresh(db_phone)
    return db_phone


@router.get("/phone-numbers", response_model=List[PhoneNumberResponse])
def list_phone_numbers(db: Session = Depends(get_db)):
    """List all registered phone numbers"""
    return db.query(PhoneNumber).all()


@router.get(
    "/phone-numbers/available", response_model=List[PhoneNumberResponse]
)
def list_available_phone_numbers(db: Session = Depends(get_db)):
    """List available phone numbers"""
    return db.query(PhoneNumber).filter(
        PhoneNumber.status == PhoneStatus.AVAILABLE
    ).all()


@router.delete("/phone-numbers/{phone_id}")
def delete_phone_number(phone_id: int, db: Session = Depends(get_db)):
    """Delete a phone number from the pool"""
    phone = db.query(PhoneNumber).filter(
        PhoneNumber.id == phone_id
    ).first()
    if not phone:
        raise HTTPException(
            status_code=404, detail="Phone number not found"
        )

    if phone.status == PhoneStatus.ASSIGNED:
        raise HTTPException(
            status_code=400, detail="Cannot delete assigned phone number"
        )

    db.delete(phone)
    db.commit()
    return {"message": "Phone number deleted"}


@router.put("/phone-numbers/{phone_id}/status")
def update_phone_status(
    phone_id: int, status: str, db: Session = Depends(get_db)
):
    """Update phone number status"""
    phone = db.query(PhoneNumber).filter(
        PhoneNumber.id == phone_id
    ).first()
    if not phone:
        raise HTTPException(
            status_code=404, detail="Phone number not found"
        )

    # Convert string to enum
    try:
        phone_status = PhoneStatus(status)
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid status value"
        )

    phone.status = phone_status
    if phone_status != PhoneStatus.ASSIGNED:
        phone.group_id = None
        phone.assigned_at = None

    db.commit()
    return {"message": f"Phone number status updated to {phone_status}"}
