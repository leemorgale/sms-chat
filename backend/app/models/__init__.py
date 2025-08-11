# Import all models to ensure they're registered with SQLAlchemy
from .models import User, Group, Message, user_groups  # noqa: F401
from .phone_pool import PhoneNumber, PhoneStatus, OTPVerification  # noqa: F401
