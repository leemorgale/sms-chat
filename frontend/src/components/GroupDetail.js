import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';

function GroupDetail({ currentUser }) {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const [group, setGroup] = useState(null);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetchGroupDetails();
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, [groupId]);

  const fetchGroupDetails = async () => {
    try {
      const response = await api.get(`/groups/${groupId}`);
      setGroup(response.data);
    } catch (err) {
      console.error('Failed to fetch group details:', err);
    }
  };

  const fetchMessages = async () => {
    try {
      const response = await api.get(`/groups/${groupId}/messages`);
      setMessages(response.data);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  };

  const handleLeaveGroup = async () => {
    try {
      await api.post(`/groups/${groupId}/leave/${currentUser.id}`);
      navigate('/groups');
    } catch (err) {
      console.error('Failed to leave group:', err);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (!group) return <div>Loading...</div>;

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2>💬 {group.name}</h2>
          <div className="meta" style={{ margin: 0 }}>
            👥 {group.user_count} {group.user_count === 1 ? 'member' : 'members'}
          </div>
        </div>
        <div>
          <button className="btn btn-secondary" onClick={() => navigate('/groups')}>
            ← Back to Groups
          </button>
          <button className="btn btn-danger" onClick={handleLeaveGroup}>
            🚪 Leave Group
          </button>
        </div>
      </div>
      
      <div style={{ background: '#e3f2fd', padding: '15px', borderRadius: '8px', marginBottom: '20px', fontSize: '14px' }}>
        <strong>📱 How to send messages:</strong>
        <ul style={{ margin: '10px 0', paddingLeft: '20px' }}>
          <li>Reply to the SMS you received when joining this group</li>
          <li>Your message will appear here and be sent to all members</li>
          <li>If you're in multiple groups, use <code>@{group.name} your message</code></li>
        </ul>
      </div>
      
      <div>
        <h3>📨 Recent Messages</h3>
        
        <div className="message-list">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>💬</div>
              <div>No messages yet!</div>
              <div style={{ fontSize: '14px', marginTop: '10px' }}>
                Send an SMS to start the conversation
              </div>
            </div>
          ) : (
            messages.reverse().map(message => (
              <div key={message.id} className="message">
                <div className="header">
                  <span className="author">👤 {message.user_name}</span>
                  <span className="time">🕐 {formatTime(message.created_at)}</span>
                </div>
                <div className="content">{message.content}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default GroupDetail;