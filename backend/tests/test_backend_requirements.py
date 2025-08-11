"""
Backend Tests for Group SMS Chat Application
Tests align with requirements from Task.md
Complete API Coverage - All Endpoints Tested
"""
import pytest
from fastapi import status
from app.models.models import User, Group
from app.models.phone_pool import OTPVerification, PhoneNumber, PhoneStatus
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

class TestUserManagement:
    """Test user account creation and management"""
    
    def test_create_user_account(self, client):
        """Test: Users can create an account with phone number and name"""
        response = client.post(
            "/api/users/",
            json={"name": "Test User", "phone_number": "+19999999999"}
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data["name"] == "Test User"
        assert data["phone_number"] == "+19999999999"
        assert "id" in data
    
    def test_duplicate_phone_number_rejected(self, client):
        """Test: System prevents duplicate phone numbers"""
        # Create first user
        client.post(
            "/api/users/",
            json={"name": "First User", "phone_number": "+19999999999"}
        )
        
        # Try to create second user with same phone
        response = client.post(
            "/api/users/",
            json={"name": "Second User", "phone_number": "+19999999999"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_user_by_phone(self, client, test_user):
        """Test: Can retrieve user by phone number"""
        response = client.get(f"/api/users/phone/{test_user.phone_number}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["phone_number"] == test_user.phone_number

class TestGroupManagement:
    """Test group creation and management"""
    
    def test_create_group(self, client):
        """Test: Users can create a new group chat with a name"""
        response = client.post(
            "/api/groups/",
            json={"name": "Test Group Chat"}
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert data["name"] == "Test Group Chat"
        assert "id" in data
        assert data["user_count"] == 0
    
    def test_search_groups(self, client, test_group):
        """Test: Users can search for group chats"""
        # Search with matching term
        response = client.get("/api/groups/?search=Test")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert any(g["name"] == test_group.name for g in data)
        
        # Search with non-matching term
        response = client.get("/api/groups/?search=NonExistent")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(g["name"] != test_group.name for g in data)
    
    def test_list_all_groups(self, client, test_group):
        """Test: Can list all groups without search"""
        response = client.get("/api/groups/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert any(g["id"] == test_group.id for g in data)

class TestGroupMembership:
    """Test joining and leaving groups"""
    
    def test_join_group(self, client, test_user, test_group):
        """Test: Users can join an existing group"""
        response = client.post(f"/api/groups/{test_group.id}/join/{test_user.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        
        # Verify group user count increased
        response = client.get(f"/api/groups/{test_group.id}")
        assert response.json()["user_count"] == 1
    
    def test_cannot_join_twice(self, client, test_user, test_group):
        """Test: Cannot join same group twice"""
        # Join once
        client.post(f"/api/groups/{test_group.id}/join/{test_user.id}")
        
        # Try to join again
        response = client.post(f"/api/groups/{test_group.id}/join/{test_user.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_leave_group(self, client, test_user, test_group):
        """Test: Users can leave a group"""
        # First join the group
        client.post(f"/api/groups/{test_group.id}/join/{test_user.id}")
        
        # Then leave
        response = client.post(f"/api/groups/{test_group.id}/leave/{test_user.id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify group user count decreased
        response = client.get(f"/api/groups/{test_group.id}")
        assert response.json()["user_count"] == 0
    
    def test_join_multiple_groups(self, client, test_user, db):
        """Test: Users can be part of more than one chat room"""
        # Create multiple groups
        groups = []
        for i in range(3):
            group = Group(name=f"Test Group {i}")
            db.add(group)
            db.commit()
            db.refresh(group)
            groups.append(group)
            
            # Join each group
            response = client.post(f"/api/groups/{group.id}/join/{test_user.id}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify user is in all groups
        response = client.get(f"/api/users/{test_user.id}/groups")
        assert response.status_code == status.HTTP_200_OK
        user_groups = response.json()
        assert len(user_groups) == 3

class TestMessaging:
    """Test messaging functionality"""
    
    def test_get_group_messages(self, client, test_user, test_group):
        """Test: Can retrieve messages for a group"""
        # Join group first
        client.post(f"/api/groups/{test_group.id}/join/{test_user.id}")
        
        # Get messages (should be empty initially)
        response = client.get(f"/api/groups/{test_group.id}/messages")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @patch('app.services.sms_service.send_group_message')
    def test_send_message_to_group(self, mock_send_sms, client, test_user, test_group, db):
        """Test: Users can send messages to groups via web interface"""
        mock_send_sms.return_value = True
        
        # Join group first
        client.post(f"/api/groups/{test_group.id}/join/{test_user.id}")
        
        # Send message to group
        response = client.post(
            f"/api/groups/{test_group.id}/messages",
            json={
                "user_id": test_user.id,
                "group_id": test_group.id,
                "content": "Hello group!"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == "Hello group!"
        assert data["user_id"] == test_user.id
        assert data["group_id"] == test_group.id
    
    def test_sms_webhook_endpoint_exists(self, client):
        """Test: SMS webhook endpoint is available"""
        # Test that endpoint exists (even if it returns error without proper data)
        response = client.post("/api/sms/webhook")
        # Should not be 404
        assert response.status_code != status.HTTP_404_NOT_FOUND

class TestEdgeCases:
    """Test error handling and edge cases"""
    
    def test_join_nonexistent_group(self, client, test_user):
        """Test: Cannot join non-existent group"""
        response = client.post(f"/api/groups/99999/join/{test_user.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_leave_group_not_member(self, client, test_user, test_group):
        """Test: Cannot leave group if not a member"""
        response = client.post(f"/api/groups/{test_group.id}/leave/{test_user.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_nonexistent_user_operations(self, client, test_group):
        """Test: Operations with non-existent user fail appropriately"""
        # Try to join with non-existent user
        response = client.post(f"/api/groups/{test_group.id}/join/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRootAPI:
    """Test root API endpoint"""
    
    def test_root_endpoint(self, client):
        """Test: Root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Group SMS Chat API"


class TestOTPAuthentication:
    """Test OTP authentication system endpoints"""
    
    @patch('app.services.otp_service.send_otp_sms')
    def test_send_otp(self, mock_send_sms, client, db):
        """Test: Send OTP to phone number"""
        mock_send_sms.return_value = "mock-message-id"
        
        response = client.post(
            "/api/users/send-otp",
            json={"phone_number": "+1234567890"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        
        # Verify OTP record was created
        otp = db.query(OTPVerification).filter(
            OTPVerification.phone_number == "+1234567890"
        ).first()
        assert otp is not None
        assert len(otp.otp_code) == 6
        assert otp.verified == 0
        mock_send_sms.assert_called_once()
    
    @patch('app.services.otp_service.send_otp_sms')
    def test_register_with_otp_success(self, mock_send_sms, client, db):
        """Test: Register new user with valid OTP"""
        mock_send_sms.return_value = "mock-message-id"
        
        # First send OTP
        client.post(
            "/api/users/send-otp",
            json={"phone_number": "+1234567890"}
        )
        
        # Get the OTP code from database
        otp_record = db.query(OTPVerification).filter(
            OTPVerification.phone_number == "+1234567890"
        ).first()
        
        # Register with OTP
        response = client.post(
            "/api/users/register",
            json={
                "phone_number": "+1234567890",
                "name": "Test User",
                "otp_code": otp_record.otp_code
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test User"
        assert data["phone_number"] == "+1234567890"
        assert "id" in data
        
        # Verify OTP was marked as verified
        db.refresh(otp_record)
        assert otp_record.verified == 1
    
    @patch('app.services.otp_service.send_otp_sms')
    def test_register_with_invalid_otp(self, mock_send_sms, client, db):
        """Test: Register with invalid OTP fails"""
        mock_send_sms.return_value = "mock-message-id"
        
        response = client.post(
            "/api/users/register",
            json={
                "phone_number": "+1234567890",
                "name": "Test User",
                "otp_code": "123456"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Invalid or expired OTP"
    
    @patch('app.services.otp_service.send_otp_sms')
    def test_login_with_otp_success(self, mock_send_sms, client, db, test_user):
        """Test: Login existing user with valid OTP"""
        mock_send_sms.return_value = "mock-message-id"
        
        # Send OTP
        client.post(
            "/api/users/send-otp",
            json={"phone_number": test_user.phone_number}
        )
        
        # Get OTP
        otp_record = db.query(OTPVerification).filter(
            OTPVerification.phone_number == test_user.phone_number
        ).first()
        
        # Login with OTP
        response = client.post(
            "/api/users/login",
            json={
                "phone_number": test_user.phone_number,
                "otp_code": otp_record.otp_code
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["phone_number"] == test_user.phone_number


class TestCompleteUserManagement:
    """Test additional user management endpoints"""
    
    def test_get_all_users(self, client, test_user):
        """Test: Get all users"""
        response = client.get("/api/users/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(user["id"] == test_user.id for user in data)
    
    def test_get_user_by_id(self, client, test_user):
        """Test: Get user by ID"""
        response = client.get(f"/api/users/{test_user.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["name"] == test_user.name
        assert data["phone_number"] == test_user.phone_number
    
    def test_get_user_by_id_not_found(self, client):
        """Test: Get non-existent user by ID returns 404"""
        response = client.get("/api/users/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "User not found"


class TestAdminPhoneManagement:
    """Test admin phone number management endpoints"""
    
    def test_register_phone_number(self, client, db):
        """Test: Register new Twilio phone number"""
        response = client.post(
            "/api/admin/phone-numbers",
            json={
                "phone_number": "+1234567890",
                "twilio_sid": "PN123456789"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["phone_number"] == "+1234567890"
        assert data["twilio_sid"] == "PN123456789"
        assert data["status"] == "AVAILABLE"
    
    def test_list_all_phone_numbers(self, client, db):
        """Test: List all registered phone numbers"""
        # Create test phone numbers
        phone1 = PhoneNumber(
            phone_number="+1234567890",
            twilio_sid="PN123",
            status=PhoneStatus.AVAILABLE
        )
        phone2 = PhoneNumber(
            phone_number="+1234567891", 
            twilio_sid="PN124",
            status=PhoneStatus.ASSIGNED
        )
        db.add_all([phone1, phone2])
        db.commit()
        
        response = client.get("/api/admin/phone-numbers")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_list_available_phone_numbers(self, client, db):
        """Test: List only available phone numbers"""
        # Create available and assigned phone numbers
        available = PhoneNumber(
            phone_number="+1234567890",
            twilio_sid="PN123",
            status=PhoneStatus.AVAILABLE
        )
        assigned = PhoneNumber(
            phone_number="+1234567891",
            twilio_sid="PN124", 
            status=PhoneStatus.ASSIGNED
        )
        db.add_all([available, assigned])
        db.commit()
        
        response = client.get("/api/admin/phone-numbers/available")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should only return available phones
        for phone in data:
            assert phone["status"] == "AVAILABLE"
    
    def test_delete_phone_number(self, client, db):
        """Test: Delete phone number from pool"""
        # Create a phone number
        phone = PhoneNumber(
            phone_number="+1234567890",
            twilio_sid="test_sid",
            status=PhoneStatus.AVAILABLE
        )
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        response = client.delete(f"/api/admin/phone-numbers/{phone.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Phone number deleted"
        
        # Verify phone number was deleted
        deleted_phone = db.query(PhoneNumber).filter(
            PhoneNumber.id == phone.id
        ).first()
        assert deleted_phone is None
    
    def test_delete_phone_number_not_found(self, client):
        """Test: Delete non-existent phone number returns 404"""
        response = client.delete("/api/admin/phone-numbers/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Phone number not found"
    
    def test_delete_assigned_phone_number(self, client, db, test_group):
        """Test: Cannot delete assigned phone number"""
        # Create assigned phone number
        phone = PhoneNumber(
            phone_number="+1234567890",
            twilio_sid="test_sid",
            status=PhoneStatus.ASSIGNED,
            group_id=test_group.id
        )
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        response = client.delete(f"/api/admin/phone-numbers/{phone.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"] == "Cannot delete assigned phone number"
    
    def test_update_phone_status(self, client, db):
        """Test: Update phone number status"""
        # Create a phone number
        phone = PhoneNumber(
            phone_number="+1234567890",
            twilio_sid="test_sid",
            status=PhoneStatus.AVAILABLE
        )
        db.add(phone)
        db.commit()
        db.refresh(phone)
        
        response = client.put(
            f"/api/admin/phone-numbers/{phone.id}/status",
            params={"status": "INACTIVE"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Phone number status updated" in data["message"]
        
        # Verify status was updated
        db.refresh(phone)
        assert phone.status == PhoneStatus.INACTIVE
    
    def test_update_phone_status_not_found(self, client):
        """Test: Update status of non-existent phone number returns 404"""
        response = client.put(
            "/api/admin/phone-numbers/99999/status",
            params={"status": "INACTIVE"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Phone number not found"