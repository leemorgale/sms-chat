import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, LogOut, Users, MessageSquare, Clock, User as UserIcon, Send } from 'lucide-react';
import api from '../services/api';
import { User, Group, Message } from '../types';

interface GroupDetailProps {
  currentUser: User;
}

interface ExtendedMessage extends Message {
  user_name: string;
}

function GroupDetail({ currentUser }: GroupDetailProps) {
  const { groupId } = useParams<{ groupId: string }>();
  const navigate = useNavigate();
  const [group, setGroup] = useState<Group | null>(null);
  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  // Move function definitions BEFORE useEffect
  const fetchGroupDetails = useCallback(async () => {
    try {
      const response = await api.get<Group>(`/groups/${groupId}`);
      setGroup(response.data);
    } catch (err) {
      console.error('Failed to fetch group details:', err);
    } finally {
      setIsLoading(false);
    }
  }, [groupId]);

  const fetchMessages = useCallback(async () => {
    try {
      console.log('Fetching messages for group:', groupId); // Debug log
      const response = await api.get<ExtendedMessage[]>(`/groups/${groupId}/messages`);
      console.log('Messages response:', response.data); // Debug log
      setMessages(response.data);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  }, [groupId]);

  useEffect(() => {
    fetchGroupDetails();
    fetchMessages();
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, [groupId, fetchGroupDetails, fetchMessages]);

  const handleLeaveGroup = async () => {
    if (confirm('Are you sure you want to leave this group?')) {
      try {
        await api.post(`/groups/${groupId}/leave/${currentUser.id}`);
        navigate('/groups');
      } catch (err) {
        console.error('Failed to leave group:', err);
      }
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || isSending) return;

    setIsSending(true);
    try {
      console.log('Sending message:', { content: newMessage, user_id: currentUser.id }); // Debug log
      await api.post(`/groups/${groupId}/messages`, {
        content: newMessage,
        user_id: currentUser.id
      });
      setNewMessage('');
      fetchMessages();
    } catch (err) {
      console.error('Failed to send message:', err);
      alert('Failed to send message. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + 
             date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!group) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Group not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/groups')}
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="h-6 w-6" />
            </button>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{group.name}</h2>
              <div className="flex items-center text-sm text-gray-600 mt-1">
                <Users className="h-4 w-4 mr-1" />
                <span>{group.user_count} {group.user_count === 1 ? 'member' : 'members'}</span>
              </div>
            </div>
          </div>
          <button
            onClick={handleLeaveGroup}
            className="flex items-center px-4 py-2 border border-red-300 rounded-md text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Leave Group
          </button>
        </div>
        
        {/* Message Input Form */}
        <form onSubmit={handleSendMessage} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                Send a message
              </label>
              <input
                type="text"
                id="message"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={isSending}
              />
            </div>
            <button
              type="submit"
              disabled={!newMessage.trim() || isSending}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="h-4 w-4 mr-2" />
              {isSending ? 'Sending...' : 'Send'}
            </button>
          </div>
          <p className="mt-2 text-xs text-gray-500">
            You can also reply to SMS messages to send messages to this group
          </p>
        </form>
      </div>

      {/* Messages */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <MessageSquare className="h-5 w-5 mr-2 text-indigo-600" />
          Recent Messages
        </h3>
        
        <div className="space-y-3 max-h-[500px] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-center py-16">
              <MessageSquare className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 font-medium mb-2">No messages yet!</p>
              <p className="text-sm text-gray-400">Send an SMS to start the conversation</p>
            </div>
          ) : (
            [...messages].reverse().map(message => (
              <div key={message.id} className="bg-gradient-to-r from-gray-50 to-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center">
                    <div className="bg-indigo-100 rounded-full p-2 mr-3">
                      <UserIcon className="h-4 w-4 text-indigo-600" />
                    </div>
                    <span className="font-semibold text-gray-900">{message.user_name}</span>
                  </div>
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="h-3 w-3 mr-1" />
                    {formatTime(message.created_at)}
                  </div>
                </div>
                <div className="pl-11 text-gray-700">{message.content}</div>
              </div>
            ))
          )}
        </div>
        
        {messages.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-center text-sm text-gray-500">
              <Send className="h-4 w-4 mr-2" />
              Reply to your SMS to send a message
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default GroupDetail;