import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MessageSquare, LogOut, Smartphone } from 'lucide-react';
import Register from './components/Register';
import GroupList from './components/GroupList';
import GroupDetail from './components/GroupDetail';
import { User } from './types';

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Failed to parse user from localStorage:', error);
        localStorage.removeItem('currentUser');
      }
    }
  }, []);

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('currentUser', JSON.stringify(user));
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUser');
  };

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <MessageSquare className="h-8 w-8 text-indigo-600" />
                <h1 className="text-2xl font-bold text-gray-900">Group SMS Chat</h1>
              </div>
              {currentUser && (
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{currentUser.name}</div>
                    <div className="text-xs text-gray-500 flex items-center">
                      <Smartphone className="h-3 w-3 mr-1" />
                      {currentUser.phone_number}
                    </div>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="container mx-auto px-4 py-8">
          {!currentUser && (
            <div className="mb-6 bg-indigo-600 text-white px-6 py-4 rounded-lg shadow-md">
              <div className="flex items-center">
                <MessageSquare className="h-5 w-5 mr-2" />
                <span className="font-semibold">Demo Mode:</span>
                <span className="ml-2">Try with any phone number (SMS will be mocked)</span>
              </div>
            </div>
          )}
          
          <Routes>
            <Route 
              path="/" 
              element={currentUser ? <Navigate to="/groups" /> : <Register onLogin={handleLogin} />} 
            />
            <Route 
              path="/groups" 
              element={currentUser ? <GroupList currentUser={currentUser} /> : <Navigate to="/" />} 
            />
            <Route 
              path="/groups/:groupId" 
              element={currentUser ? <GroupDetail currentUser={currentUser} /> : <Navigate to="/" />} 
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;