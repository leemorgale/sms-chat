from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, Group, Message
from app.models.schemas import MessageCreate
from app.services.sms_service import send_group_message, parse_sms_command

router = APIRouter()

@router.post("/webhook")
def handle_sms_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.phone_number == From).first()
    if not user:
        return {"message": "User not registered"}
    
    active_groups = user.groups
    if not active_groups:
        return {"message": "You are not in any groups. Join a group first!"}
    
    if len(active_groups) == 1:
        group = active_groups[0]
    else:
        group_name, message_body = parse_sms_command(Body)
        if group_name:
            group = next((g for g in active_groups if g.name.lower() == group_name.lower()), None)
            if not group:
                return {"message": f"Group '{group_name}' not found"}
            Body = message_body
        else:
            group = active_groups[0]
    
    db_message = Message(
        content=Body,
        user_id=user.id,
        group_id=group.id
    )
    db.add(db_message)
    db.commit()
    
    for member in group.users:
        if member.id != user.id:
            send_group_message(member.phone_number, user.name, Body, group.name)
    
    return {"message": "Message sent to group"}