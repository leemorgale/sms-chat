"""
Test all required features from the coding challenge task
"""
import pytest
from fastapi.testclient import TestClient


class TestAPIRequiredFeatures:
    """Test all API features required by the task"""
    
    def test_users_can_create_account_with_phone_and_name(self, client):
        """Users can create an account, which includes a phone number and a name."""
        response = client.post("/api/users/", json={
            "name": "John Doe",
            "phone_number": "+1234567890"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["phone_number"] == "+1234567890"
        assert "id" in data
        assert "created_at" in data

    def test_users_can_search_for_group_chats(self, client):
        """Users can search for group chats created on the service"""
        # Create test groups
        client.post("/api/groups/", json={"name": "Python Developers"})
        client.post("/api/groups/", json={"name": "JavaScript Developers"})
        client.post("/api/groups/", json={"name": "React Users"})
        
        # Search for groups
        response = client.get("/api/groups/?search=Python")
        assert response.status_code == 200
        groups = response.json()
        assert len(groups) == 1
        assert groups[0]["name"] == "Python Developers"
        
        # Search for multiple matches
        response = client.get("/api/groups/?search=Developers")
        assert response.status_code == 200
        groups = response.json()
        assert len(groups) == 2

    def test_users_can_create_new_group_chat_with_name(self, client):
        """Users can create a new group chat, and give it a name"""
        response = client.post("/api/groups/", json={
            "name": "My Test Group"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My Test Group"
        assert "id" in data
        assert "created_at" in data

    def test_users_can_join_existing_group(self, client):
        """Users can join an existing group"""
        # Create user and group
        user_resp = client.post("/api/users/", json={
            "name": "Jane Doe", 
            "phone_number": "+1987654321"
        })
        user = user_resp.json()
        
        group_resp = client.post("/api/groups/", json={"name": "Test Group"})
        group = group_resp.json()
        
        # Join group
        response = client.post(f"/api/groups/{group['id']}/join/{user['id']}")
        assert response.status_code == 200
        assert "joined group" in response.json()["message"].lower()
        
        # Verify user count increased
        group_check = client.get(f"/api/groups/{group['id']}")
        assert group_check.json()["user_count"] == 1

    def test_users_can_leave_group(self, client):
        """Users can leave a group."""
        # Create user and group
        user_resp = client.post("/api/users/", json={
            "name": "Bob Smith", 
            "phone_number": "+1555666777"
        })
        user = user_resp.json()
        
        group_resp = client.post("/api/groups/", json={"name": "Leavable Group"})
        group = group_resp.json()
        
        # Join then leave
        client.post(f"/api/groups/{group['id']}/join/{user['id']}")
        response = client.post(f"/api/groups/{group['id']}/leave/{user['id']}")
        
        assert response.status_code == 200
        assert "left group" in response.json()["message"].lower()


class TestSMSRequiredFeatures:
    """Test SMS features required by the task"""
    
    def test_welcome_sms_sent_on_group_join(self, client):
        """Upon joining a group on the website, users should receive an SMS welcoming them"""
        # Create user and group
        user_resp = client.post("/api/users/", json={
            "name": "SMS User", 
            "phone_number": "+1111222333"
        })
        user = user_resp.json()
        
        group_resp = client.post("/api/groups/", json={"name": "SMS Group"})
        group = group_resp.json()
        
        # Join group (should trigger welcome SMS)
        response = client.post(f"/api/groups/{group['id']}/join/{user['id']}")
        assert response.status_code == 200
        # In mock mode, SMS is logged - we can't easily test this without checking logs
        # But the endpoint should complete successfully

    def test_sms_webhook_processes_incoming_messages(self, client):
        """Users should be able to text this number to send a message to the chat"""
        # Create user and group
        user_resp = client.post("/api/users/", json={
            "name": "Texter", 
            "phone_number": "+1999888777"
        })
        user = user_resp.json()
        
        group_resp = client.post("/api/groups/", json={"name": "Chat Group"})
        group = group_resp.json()
        
        # Join group first
        client.post(f"/api/groups/{group['id']}/join/{user['id']}")
        
        # Simulate incoming SMS via webhook
        sms_data = {
            "From": "+1999888777",
            "Body": "Hello everyone!",
            "To": "+1234567890"
        }
        response = client.post("/api/sms/webhook", data=sms_data)
        assert response.status_code == 200
        
        # Check that message was stored
        messages = client.get(f"/api/groups/{group['id']}/messages")
        assert messages.status_code == 200
        message_list = messages.json()
        assert len(message_list) == 1
        assert message_list[0]["content"] == "Hello everyone!"
        assert message_list[0]["user_name"] == "Texter"

    def test_multiple_chat_rooms_support(self, client):
        """Users should be able to be part of more than one chat room at a time"""
        # Create user
        user_resp = client.post("/api/users/", json={
            "name": "Multi User", 
            "phone_number": "+1444555666"
        })
        user = user_resp.json()
        
        # Create two groups
        group1_resp = client.post("/api/groups/", json={"name": "Group One"})
        group1 = group1_resp.json()
        
        group2_resp = client.post("/api/groups/", json={"name": "Group Two"})
        group2 = group2_resp.json()
        
        # Join both groups
        join1 = client.post(f"/api/groups/{group1['id']}/join/{user['id']}")
        join2 = client.post(f"/api/groups/{group2['id']}/join/{user['id']}")
        
        assert join1.status_code == 200
        assert join2.status_code == 200
        
        # Test targeted messaging with @groupname syntax
        sms_data = {
            "From": "+1444555666",
            "Body": "@Group One Hello Group One!",
            "To": "+1234567890"
        }
        response = client.post("/api/sms/webhook", data=sms_data)
        assert response.status_code == 200
        
        # Check message went to correct group
        group1_messages = client.get(f"/api/groups/{group1['id']}/messages")
        group2_messages = client.get(f"/api/groups/{group2['id']}/messages")
        
        assert len(group1_messages.json()) == 1
        assert len(group2_messages.json()) == 0
        assert group1_messages.json()[0]["content"] == "Hello Group One!"


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_duplicate_phone_number_registration(self, client):
        """Cannot register same phone number twice"""
        client.post("/api/users/", json={
            "name": "First User",
            "phone_number": "+1111111111"
        })
        
        response = client.post("/api/users/", json={
            "name": "Second User", 
            "phone_number": "+1111111111"
        })
        assert response.status_code == 400

    def test_join_nonexistent_group(self, client):
        """Joining non-existent group returns 404"""
        user_resp = client.post("/api/users/", json={
            "name": "Test User",
            "phone_number": "+1222333444"
        })
        user = user_resp.json()
        
        response = client.post(f"/api/groups/999/join/{user['id']}")
        assert response.status_code == 404

    def test_sms_from_unregistered_user(self, client):
        """SMS from unregistered phone number handled gracefully"""
        sms_data = {
            "From": "+1000000000",  # Not registered
            "Body": "Hello!",
            "To": "+1234567890"
        }
        response = client.post("/api/sms/webhook", data=sms_data)
        assert response.status_code == 200
        assert "not registered" in response.json()["message"].lower()