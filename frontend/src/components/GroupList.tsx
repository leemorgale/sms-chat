import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Plus, Search, Eye, Rocket, CheckCircle } from 'lucide-react';
import api from '../services/api';
import { User, Group } from '../types';

interface GroupListProps {
  currentUser: User;
}

function GroupList({ currentUser }: GroupListProps) {
  const [groups, setGroups] = useState<Group[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [newGroupName, setNewGroupName] = useState('');
  const [userGroups, setUserGroups] = useState<Set<number>>(new Set());
  const [isCreating, setIsCreating] = useState(false);
  const navigate = useNavigate();

  const fetchGroups = useCallback(async () => {
    try {
      const response = await api.get<Group[]>('/groups/', {
        params: searchTerm ? { search: searchTerm } : {}
      });
      setGroups(response.data);
    } catch (err) {
      console.error('Failed to fetch groups:', err);
    }
  }, [searchTerm]);

  const fetchUserGroups = useCallback(async () => {
    if (!currentUser) return;
    
    try {
      const response = await api.get<number[]>(`/users/${currentUser.id}/groups`);
      setUserGroups(new Set(response.data));
    } catch (err) {
      console.error('Failed to fetch user groups:', err);
    }
  }, [currentUser]);

  useEffect(() => {
    fetchGroups();
    if (currentUser) {
      fetchUserGroups();
    }
  }, [currentUser, fetchGroups, fetchUserGroups]);

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    try {
      await api.post('/groups/', { name: newGroupName });
      setNewGroupName('');
      fetchGroups();
    } catch (err) {
      console.error('Failed to create group:', err);
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinGroup = async (groupId: number) => {
    try {
      await api.post(`/groups/${groupId}/join/${currentUser.id}`);
      alert('Successfully joined group! You will receive an SMS welcome message.');
      
      setUserGroups(prev => new Set([...prev, groupId]));
      navigate(`/groups/${groupId}`);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err && 
          (err as { response?: { status?: number } }).response?.status === 400) {
        alert('You are already in this group.');
        navigate(`/groups/${groupId}`);
      } else {
        console.error('Failed to join group:', err);
        alert('Failed to join group. Please try again.');
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Create New Group */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center mb-4">
          <Plus className="h-6 w-6 text-indigo-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Create New Group</h2>
        </div>
        <p className="text-gray-600 mb-4">
          Start a new SMS group chat that others can join
        </p>
        <form onSubmit={handleCreateGroup} className="flex gap-3">
          <input
            type="text"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            placeholder="Enter group name (e.g., 'Team Updates', 'Book Club')"
            required
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={isCreating}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Plus className="h-5 w-5" />
          </button>
        </form>
      </div>

      {/* Browse Groups */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center mb-4">
          <Search className="h-6 w-6 text-indigo-600 mr-2" />
          <h2 className="text-xl font-bold text-gray-900">Browse & Join Groups</h2>
        </div>
        
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyUp={fetchGroups}
            placeholder="Search groups by name..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        {groups.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            {searchTerm ? 
              `No groups found matching "${searchTerm}"` : 
              'No groups available. Create the first one!'
            }
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {groups.map(group => {
              const isMember = userGroups.has(group.id);
              
              return (
                <div key={group.id} className="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">{group.name}</h3>
                    {isMember && (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    )}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600 mb-4">
                    <Users className="h-4 w-4 mr-1" />
                    <span>
                      {group.user_count} {group.user_count === 1 ? 'member' : 'members'}
                    </span>
                  </div>
                  
                  {isMember ? (
                    <button 
                      className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      onClick={() => navigate(`/groups/${group.id}`)}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      View Group
                    </button>
                  ) : (
                    <button 
                      className="w-full flex items-center justify-center px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white text-sm font-medium rounded-md hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all"
                      onClick={() => handleJoinGroup(group.id)}
                    >
                      <Rocket className="h-4 w-4 mr-2" />
                      Join Group
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default GroupList;