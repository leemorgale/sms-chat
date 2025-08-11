from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User, Group, Message
from app.models.phone_pool import PhoneNumber, PhoneStatus
from app.services.sms_service import send_group_message, parse_sms_command

router = APIRouter()


@router.post("/webhook")
def handle_sms_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    To: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.phone_number == From).first()
    if not user:
        return {"message": "User not registered"}

    target_group = None
    group_phone_for_sending = None
    content = Body

    # Route by assigned pool phone if available
    phone_record = db.query(PhoneNumber).filter(
        PhoneNumber.phone_number == To
    ).first()
    if (
        phone_record
        and phone_record.status == PhoneStatus.ASSIGNED
        and phone_record.group_id
    ):
        target_group = db.query(Group).filter(
            Group.id == phone_record.group_id
        ).first()
        if target_group and user not in target_group.users:
            return {
                "message": (
                    f"You are not a member of the "
                    f"'{target_group.name}' group"
                )
            }
        group_phone_for_sending = To

    # Fallback: support @"Group Name" or single-group routing
    if not target_group:
        group_name, stripped = parse_sms_command(Body)
        if group_name:
            for g in list(user.groups):
                if g.name.lower() == group_name.lower():
                    target_group = g
                    content = stripped
                    break
            if not target_group:
                return {
                    "message": (
                        f"Group '{group_name}' not found or you are "
                        f"not a member"
                    )
                }
        else:
            if len(user.groups) == 1:
                target_group = user.groups[0]
            else:
                return {
                    "message": (
                        'Multiple groups detected. Prefix message with '
                        '@"Group Name" to specify destination.'
                    )
                }

    if not target_group:
        return {"message": "Group not found for this number"}

    db_message = Message(
        content=content, user_id=user.id, group_id=target_group.id
    )
    db.add(db_message)
    db.commit()

    if not group_phone_for_sending and target_group.phone_number_rel:
        group_phone_for_sending = (
            target_group.phone_number_rel.phone_number
        )

    for member in target_group.users:
        if member.id != user.id:
            send_group_message(
                member.phone_number,
                user.name,
                content,
                target_group.name,
                group_phone_for_sending,
            )

    return {"message": f"Message sent to {target_group.name} group"}
