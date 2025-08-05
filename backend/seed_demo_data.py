#!/usr/bin/env python3
"""
Demo data seeder for SMS Chat application
Run this to populate the database with sample users, groups, and messages for testing
"""

from sqlalchemy.orm import sessionmaker
from app.db.database import engine, Base
from app.models.models import User, Group, Message
from datetime import datetime, timedelta
import random

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def seed_demo_data():
    print("🌱 Seeding demo data...")
    
    # Clear existing data
    db.query(Message).delete()
    db.query(User).delete()
    db.query(Group).delete()
    db.commit()
    
    # Create sample users
    users_data = [
        {"name": "Alice Johnson", "phone_number": "+1555001001"},
        {"name": "Bob Smith", "phone_number": "+1555001002"},
        {"name": "Carol Davis", "phone_number": "+1555001003"},
        {"name": "David Wilson", "phone_number": "+1555001004"},
        {"name": "Emma Brown", "phone_number": "+1555001005"},
        {"name": "Frank Miller", "phone_number": "+1555001006"},
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"✅ Created {len(users)} users")
    
    # Create sample groups
    groups_data = [
        {"name": "Tech Team Updates"},
        {"name": "Book Club Discussion"},
        {"name": "Weekend Plans"},
        {"name": "Recipe Sharing"},
        {"name": "Study Group - Python"},
        {"name": "Movie Night Planning"},
        {"name": "Fitness Accountability"},
        {"name": "Travel Buddies"},
    ]
    
    groups = []
    for group_data in groups_data:
        group = Group(**group_data)
        db.add(group)
        groups.append(group)
    
    db.commit()
    print(f"✅ Created {len(groups)} groups")
    
    # Add users to groups (randomly)
    for group in groups:
        # Each group gets 2-4 random members
        num_members = random.randint(2, 4)
        group_members = random.sample(users, num_members)
        group.users.extend(group_members)
    
    db.commit()
    print("✅ Added users to groups")
    
    # Create sample messages
    sample_messages = [
        "Hey everyone! Hope you're all doing well 👋",
        "Just wanted to share this cool article I found",
        "Are we still meeting tomorrow?",
        "Thanks for the great discussion yesterday!",
        "I'll be a few minutes late to the meeting",
        "Check out this awesome resource I discovered",
        "Looking forward to our next session",
        "Has anyone tried the new approach we discussed?",
        "Quick reminder about today's deadline",
        "Great work everyone on the project!",
        "Can someone send me the notes from last time?",
        "I found a solution to that problem we had",
        "This is exactly what we needed, perfect timing!",
        "Let me know if you need any help with that",
        "Awesome job on the presentation! 🎉",
    ]
    
    # Add messages to some groups
    message_count = 0
    for group in groups[:4]:  # Only add messages to first 4 groups
        num_messages = random.randint(3, 8)
        group_users = list(group.users)
        
        for i in range(num_messages):
            user = random.choice(group_users)
            content = random.choice(sample_messages)
            
            # Create messages with different timestamps
            created_at = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            message = Message(
                content=content,
                user_id=user.id,
                group_id=group.id,
                created_at=created_at
            )
            db.add(message)
            message_count += 1
    
    db.commit()
    print(f"✅ Created {message_count} sample messages")
    
    print(f"""
🎉 Demo data seeded successfully!

📊 Summary:
- {len(users)} users created
- {len(groups)} groups created  
- {message_count} messages created

🚀 Ready to demo! Try these test accounts:
- Alice Johnson: +1555001001
- Bob Smith: +1555001002
- Carol Davis: +1555001003

Or create your own account with any phone number.
    """)

if __name__ == "__main__":
    seed_demo_data()
    db.close()