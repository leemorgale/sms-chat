from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import Group, User, Message
from app.models.schemas import (
    GroupCreate, GroupResponse, MessageResponse, MessageCreate
)
from app.models.phone_pool import PhoneNumber, PhoneStatus
from app.services.sms_service import (
    send_welcome_sms, send_group_message, send_welcome_sms_with_phone
)
from datetime import datetime

router = APIRouter()


def assign_phone_to_group(group_id: int, db: Session):
    """Assign an available phone number to a group"""
    available_phone = db.query(PhoneNumber).filter(
        PhoneNumber.status == PhoneStatus.AVAILABLE
    ).first()

    if available_phone:
        available_phone.status = PhoneStatus.ASSIGNED
        available_phone.group_id = group_id
        available_phone.assigned_at = datetime.now()
        db.commit()
        return available_phone
    return None


@router.post("/", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = Group(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)

    # Try to assign a phone number to the group
    phone = assign_phone_to_group(db_group.id, db)
    if not phone:
        print(f"Warning: No available phone numbers to assign to group "
              f"{db_group.name}")

    return db_group


@router.get("/", response_model=List[GroupResponse])
def get_groups(
    search: Optional[str] = Query(None), db: Session = Depends(get_db)
):
    query = db.query(Group)
    if search:
        query = query.filter(Group.name.contains(search))

    groups = query.all()

    result = []
    for group in groups:
        group_dict = {
            "id": group.id,
            "name": group.name,
            "created_at": group.created_at,
            "user_count": len(group.users)
        }
        result.append(GroupResponse(**group_dict))

    return result


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group_dict = {
        "id": group.id,
        "name": group.name,
        "created_at": group.created_at,
        "user_count": len(group.users)
    }
    return GroupResponse(**group_dict)


@router.post("/{group_id}/join/{user_id}")
def join_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user in group.users:
        raise HTTPException(status_code=400, detail="User already in group")

    group.users.append(user)
    db.commit()

    # Create a system welcome message in the database
    welcome_message = Message(
        content=f"{user.name} joined the group!",
        user_id=user_id,
        group_id=group_id
    )
    db.add(welcome_message)
    db.commit()

    # Send welcome SMS using group's assigned phone number if available
    if group.phone_number_rel and group.phone_number_rel.phone_number:
        send_welcome_sms_with_phone(
            user.phone_number, group.name,
            group.phone_number_rel.phone_number
        )
    else:
        send_welcome_sms(user.phone_number, group.name)

    return {"message": f"User {user.name} joined group {group.name}"}


@router.post("/{group_id}/leave/{user_id}")
def leave_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user not in group.users:
        raise HTTPException(status_code=400, detail="User not in group")

    group.users.remove(user)
    db.commit()

    return {"message": f"User {user.name} left group {group.name}"}


@router.get("/{group_id}/messages", response_model=List[MessageResponse])
def get_group_messages(group_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        Message.group_id == group_id
    ).order_by(Message.created_at.desc()).limit(50).all()

    result = []
    for msg in messages:
        msg_dict = {
            "id": msg.id,
            "content": msg.content,
            "user_id": msg.user_id,
            "group_id": msg.group_id,
            "created_at": msg.created_at,
            "user_name": msg.user.name if msg.user else None
        }
        result.append(MessageResponse(**msg_dict))

    return result


@router.post("/{group_id}/messages", response_model=MessageResponse)
def send_message(
    group_id: int, message: MessageCreate, db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    user = db.query(User).filter(User.id == message.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user not in group.users:
        raise HTTPException(status_code=403, detail="User not in group")

    db_message = Message(
        content=message.content,
        user_id=message.user_id,
        group_id=group_id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Send SMS to all other group members using group's assigned phone number
    group_phone = (group.phone_number_rel.phone_number
                   if group.phone_number_rel else None)
    for member in group.users:
        if member.id != user.id:
            send_group_message(
                member.phone_number, user.name, message.content,
                group.name, group_phone
            )

    msg_dict = {
        "id": db_message.id,
        "content": db_message.content,
        "user_id": db_message.user_id,
        "group_id": db_message.group_id,
        "created_at": db_message.created_at,
        "user_name": user.name
    }
    return MessageResponse(**msg_dict)
