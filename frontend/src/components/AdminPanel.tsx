import React, { useState, useEffect } from 'react';
import { Phone, Plus, Trash2, Settings, AlertCircle, CheckCircle } from 'lucide-react';
import api from '../services/api';

interface PhoneNumber {
  id: number;
  phone_number: string;
  twilio_sid?: string;
  status: 'AVAILABLE' | 'ASSIGNED' | 'DISABLED';
  group_id?: number;
  created_at: string;
  assigned_at?: string;
}

function AdminPanel() {
  const [phoneNumbers, setPhoneNumbers] = useState<PhoneNumber[]>([]);
  const [newPhoneNumber, setNewPhoneNumber] = useState('');
  const [newTwilioSid, setNewTwilioSid] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchPhoneNumbers();
  }, []);

  const fetchPhoneNumbers = async () => {
    try {
      const response = await api.get<PhoneNumber[]>('/admin/phone-numbers');
      setPhoneNumbers(response.data);
    } catch (err) {
      setError('Failed to fetch phone numbers');
    }
  };

  const addPhoneNumber = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPhoneNumber) return;

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      await api.post('/admin/phone-numbers', {
        phone_number: newPhoneNumber,
        twilio_sid: newTwilioSid || undefined
      });
      
      setNewPhoneNumber('');
      setNewTwilioSid('');
      setSuccess('Phone number added successfully!');
      fetchPhoneNumbers();
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to add phone number');
    } finally {
      setIsLoading(false);
    }
  };

  const deletePhoneNumber = async (phoneId: number) => {
    if (!confirm('Are you sure you want to delete this phone number?')) return;

    try {
      await api.delete(`/admin/phone-numbers/${phoneId}`);
      setSuccess('Phone number deleted successfully!');
      fetchPhoneNumbers();
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to delete phone number');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE': return 'bg-green-100 text-green-800';
      case 'ASSIGNED': return 'bg-blue-100 text-blue-800';
      case 'DISABLED': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'AVAILABLE': return <CheckCircle className="h-4 w-4" />;
      case 'ASSIGNED': return <Phone className="h-4 w-4" />;
      case 'DISABLED': return <AlertCircle className="h-4 w-4" />;
      default: return null;
    }
  };

  const availableCount = phoneNumbers.filter(p => p.status === 'AVAILABLE').length;
  const assignedCount = phoneNumbers.filter(p => p.status === 'ASSIGNED').length;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white">
          <h2 className="text-2xl font-bold flex items-center">
            <Settings className="mr-3 h-6 w-6" />
            Admin Panel - Twilio Phone Management
          </h2>
          <p className="text-purple-100 mt-1">
            Manage Twilio phone numbers for group SMS routing
          </p>
        </div>

        <div className="p-6">
          {/* Status Overview */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">{availableCount}</div>
              <div className="text-green-600 text-sm">Available</div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">{assignedCount}</div>
              <div className="text-blue-600 text-sm">Assigned</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-gray-600">{phoneNumbers.length}</div>
              <div className="text-gray-600 text-sm">Total</div>
            </div>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
              {success}
            </div>
          )}

          {/* Add New Phone Number */}
          <div className="bg-gray-50 p-6 rounded-lg mb-6">
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
              <Plus className="h-5 w-5 mr-2" />
              Add Twilio Phone Number
            </h3>
            <form onSubmit={addPhoneNumber} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={newPhoneNumber}
                    onChange={(e) => setNewPhoneNumber(e.target.value)}
                    placeholder="+15551234567"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Twilio SID (Optional)
                  </label>
                  <input
                    type="text"
                    value={newTwilioSid}
                    onChange={(e) => setNewTwilioSid(e.target.value)}
                    placeholder="PN1234567890abcdef..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {isLoading ? 'Adding...' : 'Add Phone Number'}
              </button>
            </form>
          </div>

          {/* Phone Numbers List */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
              <Phone className="h-5 w-5 mr-2" />
              Registered Phone Numbers ({phoneNumbers.length})
            </h3>
            
            {phoneNumbers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Phone className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>No phone numbers registered yet</p>
                <p className="text-sm">Add your first Twilio number above</p>
              </div>
            ) : (
              <div className="space-y-3">
                {phoneNumbers.map((phone) => (
                  <div key={phone.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Phone className="h-5 w-5 text-gray-400" />
                        <div>
                          <div className="font-mono font-medium">{phone.phone_number}</div>
                          {phone.twilio_sid && (
                            <div className="text-sm text-gray-500">
                              SID: {phone.twilio_sid.substring(0, 20)}...
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 ${getStatusColor(phone.status)}`}>
                          {getStatusIcon(phone.status)}
                          <span>{phone.status}</span>
                        </span>
                        
                        {phone.group_id && (
                          <span className="text-sm text-gray-500">
                            Group #{phone.group_id}
                          </span>
                        )}
                        
                        {phone.status !== 'ASSIGNED' && (
                          <button
                            onClick={() => deletePhoneNumber(phone.id)}
                            className="text-red-600 hover:text-red-800 p-1"
                            title="Delete phone number"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <div className="mt-2 text-xs text-gray-500">
                      Created: {new Date(phone.created_at).toLocaleDateString()}
                      {phone.assigned_at && (
                        <span className="ml-4">
                          Assigned: {new Date(phone.assigned_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Instructions */}
          <div className="mt-8 bg-blue-50 p-6 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">📘 How it works:</h4>
            <ul className="text-blue-700 text-sm space-y-1">
              <li>• Add Twilio phone numbers to the pool</li>
              <li>• Numbers are automatically assigned to new groups</li>
              <li>• Each group gets its own SMS number for routing</li>
              <li>• Users text the group's number to send messages</li>
              <li>• When pool is empty, groups share numbers with @group syntax</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminPanel;