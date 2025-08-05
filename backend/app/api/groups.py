from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import Group, User, Message
from app.models.schemas import GroupCreate, GroupResponse, MessageResponse
from app.services.sms_service import send_welcome_sms

router = APIRouter()

@router.post("/", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = Group(name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/", response_model=List[GroupResponse])
def get_groups(search: Optional[str] = Query(None), db: Session = Depends(get_db)):
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
    messages = db.query(Message).filter(Message.group_id == group_id).order_by(Message.created_at.desc()).limit(50).all()
    
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