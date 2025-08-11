import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.db.database import Base, get_db
from app.main import app
from app.models.models import User, Group, Message, user_groups
from app.models.phone_pool import PhoneNumber, OTPVerification
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use separate test database
SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://smsuser:smspass@localhost:5432/sms_chat_test_db")

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override the get_db dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables in test database once per session"""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Debug: Check what tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Test database tables created: {tables}")
    
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db():
    """Get database session for tests"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function", autouse=True)
def clean_database(db):
    """Clean the database before and after each test - complete cleanup to avoid interdependencies"""
    
    def clean_all_test_data():
        """Complete cleanup of all test data"""
        try:
            # Delete all messages (no foreign key constraints)
            db.query(Message).delete(synchronize_session=False)
            
            # Delete all user_groups relationships
            db.execute(text("DELETE FROM user_groups"))
            
            # Delete all phone numbers (they reference groups)
            db.query(PhoneNumber).delete(synchronize_session=False)
            
            # Delete all OTP verifications
            db.query(OTPVerification).delete(synchronize_session=False)
            
            # Delete all groups (after phone numbers and user_groups are deleted)
            db.query(Group).delete(synchronize_session=False)
            
            # Delete all users (after user_groups are deleted)
            db.query(User).delete(synchronize_session=False)
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Database cleanup error: {e}")
    
    # Clean before test
    clean_all_test_data()
    
    yield
    
    # Clean after test 
    clean_all_test_data()

@pytest.fixture(scope="function")
def client(clean_database):
    """Create test client"""
    app.dependency_overrides[get_db] = override_get_db
    os.environ["MOCK_SMS"] = "true"
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear dependency overrides after test
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(name="Test User", phone_number="+19999999999")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_group(db):
    """Create a test group"""
    group = Group(name="Test Group")
    db.add(group)
    db.commit()
    db.refresh(group)
    return group