import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

function GroupList({ currentUser }) {
  const [groups, setGroups] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [newGroupName, setNewGroupName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups/', {
        params: searchTerm ? { search: searchTerm } : {}
      });
      setGroups(response.data);
    } catch (err) {
      console.error('Failed to fetch groups:', err);
    }
  };

  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      await api.post('/groups/', { name: newGroupName });
      setNewGroupName('');
      fetchGroups();
    } catch (err) {
      console.error('Failed to create group:', err);
    }
  };

  const handleJoinGroup = async (groupId) => {
    try {
      await api.post(`/groups/${groupId}/join/${currentUser.id}`);
      alert('Successfully joined group! You will receive an SMS welcome message.');
      navigate(`/groups/${groupId}`);
    } catch (err) {
      if (err.response?.status === 400) {
        alert('You are already in this group.');
        navigate(`/groups/${groupId}`);
      } else {
        console.error('Failed to join group:', err);
      }
    }
  };

  return (
    <div>
      <div className="card">
        <h2>🆕 Create New Group</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Start a new SMS group chat that others can join
        </p>
        <form onSubmit={handleCreateGroup}>
          <div className="form-row">
            <div className="form-group">
              <input
                type="text"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                placeholder="Enter group name (e.g., 'Team Updates', 'Book Club')"
                required
              />
            </div>
            <button type="submit" className="btn btn-success">
              ➕ Create Group
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h2>🔍 Browse & Join Groups</h2>
        <div className="form-group">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyUp={fetchGroups}
            placeholder="🔎 Search groups by name..."
          />
        </div>

        {groups.length === 0 ? (
          <div className="empty-state">
            {searchTerm ? 
              `No groups found matching "${searchTerm}"` : 
              'No groups available. Create the first one!'
            }
          </div>
        ) : (
          <div className="group-list">
            {groups.map(group => (
              <div key={group.id} className="group-card">
                <h3>💬 {group.name}</h3>
                <div className="meta">
                  {group.user_count} {group.user_count === 1 ? 'member' : 'members'}
                </div>
                <button 
                  className="btn btn-primary" 
                  onClick={() => handleJoinGroup(group.id)}
                >
                  🚀 Join Group
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default GroupList;